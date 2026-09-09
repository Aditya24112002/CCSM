from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import IntakeRequest, IntakeResponse
from .services.demo_extractor import extract_demo


app = FastAPI(title="AIVOA Complaint Management API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ccms-api", "mode": "demo"}


@app.post("/api/complaints/intake", response_model=IntakeResponse)
def intake_complaint(request: IntakeRequest) -> IntakeResponse:
    return extract_demo(request)
