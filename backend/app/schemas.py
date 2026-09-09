from pydantic import BaseModel, Field


class ComplaintData(BaseModel):
    source: str = ""
    customerName: str = ""
    productName: str = ""
    strength: str = ""
    batchNumber: str = ""
    manufacturingDate: str = ""
    expiryDate: str = ""
    quantity: str = ""
    complaintType: str = ""
    complaintDate: str = ""
    description: str = ""
    severity: str = ""
    priority: str = ""


class RiskAssessment(BaseModel):
    severity: str = "Major"
    priority: str = "High"
    recommendedAction: str = "Route to QA investigation and issue replacement."


class IntakeRequest(BaseModel):
    message: str = Field(min_length=1)
    sourceFile: str = ""
    existingComplaint: ComplaintData | None = None


class IntakeResponse(BaseModel):
    complaint: ComplaintData
    riskAssessment: RiskAssessment
    changedFields: list[str]
    sourceFile: str = ""
    mode: str = "demo"
