import json
import logging

from fastapi import FastAPI, File, Form, UploadFile
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
    record = ComplaintRecord(
        complaint_json=request.complaint.model_dump_json(),
        assessment_json=request.riskAssessment.model_dump_json(),
        original_text=request.originalText,
        source_file=request.sourceFile,
        mode=request.mode,
    )
    with SessionLocal() as session:
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
            createdAt=record.created_at.isoformat(),
        )
