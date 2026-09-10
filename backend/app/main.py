import json
import logging
import hashlib

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import SessionLocal, create_tables
from .models import ComplaintRecord
from .schemas import ComplaintData, ComplaintRecordResponse, IntakeRequest, IntakeResponse, SaveComplaintRequest
from .services.intake_service import extract_complaint
from .services.document_parser import extract_document_text


app = FastAPI(title="AIVOA Complaint Management API", version="0.1.0")
settings = get_settings()
logger = logging.getLogger(__name__)
create_tables()


def _complaint_fingerprint(complaint: ComplaintData) -> str:
    """Identify a complaint using stable fields, excluding AI-written description."""
    stable_fields = {
        field: " ".join(str(value or "").split()).casefold()
        for field, value in complaint.model_dump().items()
        if field != "description"
    }
    return hashlib.sha256(
        json.dumps(stable_fields, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _refresh_record_fingerprints() -> None:
    """Upgrade fingerprints created by the earlier, description-sensitive logic."""
    with SessionLocal() as session:
        records = session.query(ComplaintRecord).all()
        seen: set[str] = set()
        changed = False
        for record in records:
            fingerprint = _complaint_fingerprint(
                ComplaintData.model_validate(json.loads(record.complaint_json))
            )
            if fingerprint in seen:
                logger.warning("Existing duplicate record %s retained during fingerprint upgrade", record.id)
                continue
            seen.add(fingerprint)
            if record.record_fingerprint != fingerprint:
                record.record_fingerprint = fingerprint
                changed = True
        if changed:
            session.commit()


_refresh_record_fingerprints()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ccms-api", "mode": "langgraph-groq" if settings.groq_api_key else "demo"}


@app.post("/api/complaints/intake", response_model=IntakeResponse)
def intake_complaint(request: IntakeRequest) -> IntakeResponse:
    return extract_complaint(request)


@app.post("/api/complaints/intake-file", response_model=IntakeResponse)
async def intake_complaint_file(
    file: UploadFile = File(...),
    existingComplaint: str = Form("{}"),
) -> IntakeResponse:
    content = await file.read()
    document_text = extract_document_text(file.filename or "complaint", content)
    existing = ComplaintData.model_validate(json.loads(existingComplaint))
    request = IntakeRequest(
        message=document_text or f"Extract complaint details from {file.filename}",
        sourceFile=file.filename or "complaint",
        existingComplaint=existing,
    )
    return extract_complaint(request)


@app.post("/api/complaints", response_model=ComplaintRecordResponse)
def save_complaint(request: SaveComplaintRequest) -> ComplaintRecordResponse:
    fingerprint = _complaint_fingerprint(request.complaint)
    record = ComplaintRecord(
        complaint_json=request.complaint.model_dump_json(),
        assessment_json=request.riskAssessment.model_dump_json(),
        original_text=request.originalText,
        source_file=request.sourceFile,
        mode=request.mode,
        changed_fields_json=json.dumps(request.changedFields),
        missing_fields_json=json.dumps(request.missingFields),
        record_fingerprint=fingerprint,
    )
    with SessionLocal() as session:
        existing = session.query(ComplaintRecord).filter_by(record_fingerprint=fingerprint).first()
        if existing:
            return ComplaintRecordResponse(
                id=existing.id,
                complaint=request.complaint,
                riskAssessment=request.riskAssessment,
                originalText=request.originalText,
                sourceFile=request.sourceFile,
                mode=request.mode,
                changedFields=request.changedFields,
                missingFields=request.missingFields,
                createdAt=existing.created_at.isoformat(),
                duplicate=True,
            )
        session.add(record)
        session.commit()
        session.refresh(record)
        return ComplaintRecordResponse(
            id=record.id,
            complaint=request.complaint,
            riskAssessment=request.riskAssessment,
            originalText=record.original_text,
            sourceFile=record.source_file,
            mode=record.mode,
            changedFields=request.changedFields,
            missingFields=request.missingFields,
            createdAt=record.created_at.isoformat(),
            duplicate=False,
        )


@app.get("/api/complaints", response_model=list[ComplaintRecordResponse])
def list_complaints() -> list[ComplaintRecordResponse]:
    with SessionLocal() as session:
        records = session.query(ComplaintRecord).order_by(ComplaintRecord.created_at.desc()).all()
        return [
            ComplaintRecordResponse(
                id=record.id,
                complaint=ComplaintData.model_validate(json.loads(record.complaint_json)),
                riskAssessment=json.loads(record.assessment_json),
                originalText=record.original_text,
                sourceFile=record.source_file,
                mode=record.mode,
                changedFields=json.loads(record.changed_fields_json or "[]"),
                missingFields=json.loads(record.missing_fields_json or "[]"),
                createdAt=record.created_at.isoformat(),
                duplicate=False,
            )
            for record in records
        ]


@app.delete("/api/complaints/{complaint_id}")
def delete_complaint(complaint_id: int) -> dict[str, int | bool]:
    with SessionLocal() as session:
        record = session.get(ComplaintRecord, complaint_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Complaint record not found")
        session.delete(record)
        session.commit()
    return {"deleted": True, "id": complaint_id}
