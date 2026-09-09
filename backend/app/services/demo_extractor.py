import re

from ..schemas import ComplaintData, IntakeRequest, IntakeResponse, RiskAssessment


DEMO_COMPLAINT = ComplaintData(
    source="Pharmacy",
    customerName="Apollo Pharmacy",
    productName="Amoxicillin Capsules",
    strength="500 mg",
    batchNumber="AMX240602",
    manufacturingDate="01/03/2026",
    expiryDate="28/02/2028",
    quantity="12 capsules",
    complaintType="Product quality defect",
    complaintDate="18/06/2026",
    description="Customer reported discolored capsules in a pack of Amoxicillin Capsules 500 mg.",
    severity="Major",
    priority="High",
)


def extract_demo(request: IntakeRequest) -> IntakeResponse:
    complaint = request.existingComplaint.model_copy(deep=True) if request.existingComplaint else ComplaintData()
    message = request.message.strip()
    lower = message.lower()
    changed_fields: list[str] = []

    is_edit = any(term in lower for term in ("batch", "quantity", "update", "correct"))
    if not is_edit:
        complaint = DEMO_COMPLAINT.model_copy(deep=True)
        changed_fields = list(complaint.model_fields.keys())
    else:
        batch_match = re.search(r"batch(?: number)?\s*(?:is|:)?\s*([A-Z0-9-]+)", message, re.I)
        quantity_match = re.search(r"(?:affected )?quantity\s*(?:is|:)?\s*([\w ]+)", message, re.I)
        if batch_match:
            complaint.batchNumber = batch_match.group(1)
            changed_fields.append("batchNumber")
        if quantity_match:
            complaint.quantity = quantity_match.group(1).strip(" .")
            changed_fields.append("quantity")

    return IntakeResponse(
        complaint=complaint,
        riskAssessment=RiskAssessment(severity=complaint.severity or "Major", priority=complaint.priority or "High"),
        changedFields=changed_fields,
        sourceFile=request.sourceFile,
    )
