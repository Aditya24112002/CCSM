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
    complaintCategory: str = ""
    complaintDate: str = ""
    description: str = ""


class RiskAssessment(BaseModel):
    severity: str = ""
    suggestedNextAction: str = ""
    initialRiskAssessment: str = ""


class IntakeRequest(BaseModel):
    message: str = Field(min_length=1)
    sourceFile: str = ""
    existingComplaint: ComplaintData | None = None


class IntakeResponse(BaseModel):
    complaint: ComplaintData
    riskAssessment: RiskAssessment
    changedFields: list[str]
    missingFields: list[str] = Field(default_factory=list)
    sourceFile: str = ""
    mode: str = "demo"


class SaveComplaintRequest(BaseModel):
    complaint: ComplaintData
    riskAssessment: RiskAssessment
    originalText: str = ""
    sourceFile: str = ""
    mode: str = "demo"
    changedFields: list[str] = Field(default_factory=list)
    missingFields: list[str] = Field(default_factory=list)


class ComplaintRecordResponse(SaveComplaintRequest):
    id: int
    createdAt: str
    duplicate: bool = False
