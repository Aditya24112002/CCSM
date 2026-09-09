import re
from datetime import date, datetime

from ..schemas import ComplaintData, IntakeRequest, IntakeResponse, RiskAssessment
from .date_resolution import extract_relative_date_patch, format_local_today


DEMO_COMPLAINT = ComplaintData(
    source="Pharmacy",
    customerName="Apollo Pharmacy",
    productName="Amoxicillin Capsules",
    strength="500 mg",
    batchNumber="AMX240602",
    manufacturingDate="01/03/2026",
    expiryDate="28/02/2028",
    quantity="12 capsules",
    complaintCategory="Product Quality Issue",
    complaintDate="18/06/2026",
    description="Customer reported discolored capsules in a pack of Amoxicillin Capsules 500 mg.",
)

REQUIRED_FIELDS = [
    "customerName", "productName", "strength", "batchNumber",
    "manufacturingDate", "expiryDate", "complaintDate", "description",
    "complaintCategory",
]


def extract_demo(request: IntakeRequest) -> IntakeResponse:
    complaint = request.existingComplaint.model_copy(deep=True) if request.existingComplaint else ComplaintData()
    message = re.sub(r"&#x[0-9a-fA-F]+;|&#\d+;", " ", request.message.strip())
    lower = message.lower()
    changed_fields: list[str] = []
    identity_patch = extract_identity_patch(message)

    is_edit = bool(re.search(r"\b(?:sorry|actually|update|updated|correct|change|replace)\b", lower))
    if not is_edit:
        complaint = _extract_initial_complaint(message, complaint)
        changed_fields = [field for field in ComplaintData.model_fields if getattr(complaint, field)]
    else:
        batch_match = re.search(r"batch(?: number)?\s*(?:is|:)?\s*([\w-]+)", message, re.I)
        quantity_match = re.search(r"(?:affected )?quantity\s*(?:is|:)?\s*([\w ]+)", message, re.I)
        if batch_match:
            complaint.batchNumber = batch_match.group(1)
            changed_fields.append("batchNumber")
        if quantity_match:
            complaint.quantity = quantity_match.group(1).strip(" .")
            changed_fields.append("quantity")
        for field, value in extract_correction_patch(message).items():
            setattr(complaint, field, value)
            changed_fields.append(field)

    for field, value in extract_relative_date_patch(message).items():
        setattr(complaint, field, value)
        if field not in changed_fields:
            changed_fields.append(field)
    for field, value in identity_patch.items():
        setattr(complaint, field, value)
        if field not in changed_fields:
            changed_fields.append(field)

    if not complaint.complaintDate:
        complaint.complaintDate = format_local_today()
        changed_fields.append("complaintDate")
    if not complaint.complaintCategory:
        complaint.complaintCategory = _infer_category(message)
        changed_fields.append("complaintCategory")
    if not complaint.description:
        complaint.description = _professional_description(complaint, message)
        changed_fields.append("description")
    if not complaint.source:
        source = _infer_source(message)
        if source:
            complaint.source = source
            changed_fields.append("source")
    severity, action, risk = _assessment(complaint, message)
    return IntakeResponse(
        complaint=complaint,
        riskAssessment=RiskAssessment(severity=severity, suggestedNextAction=action, initialRiskAssessment=risk),
        changedFields=changed_fields,
        missingFields=[field for field in REQUIRED_FIELDS if not getattr(complaint, field)],
        sourceFile=request.sourceFile,
        mode="demo",
    )


def _format_date(value: str) -> str:
    for pattern in ("%d %B %Y", "%d %b %Y", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value.strip(), pattern).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return ""


def _extract_initial_complaint(message: str, existing: ComplaintData) -> ComplaintData:
    complaint = existing.model_copy(deep=True)
    customer = re.search(r"\bmy name is\s+([A-Za-z][A-Za-z .'-]*?)(?=\s+(?:and|would|is|here|from|about)\b|\s*[.,!]|$)", message, re.I)
    if not customer:
        customer = re.search(r"\bI am\s+([A-Za-z][A-Za-z .'-]*?)(?=\s*(?:[.,!]|$|\bI am here\b))", message, re.I)
    product = re.search(r"\b(?:with|about|regarding)\s+(?:product\s+)?([A-Za-z][A-Za-z0-9 -]*?)(?=\s+\d+(?:\.\d+)?\s*(?:milligrams?|mg|grams?|g|mL|ml)\b|\s+purchased\b|\s+from\b|\s+batch\b|[.,!]|$)", message, re.I)
    if not product:
        product = re.search(r"\bproduct\s+([\w-]+)", message, re.I)
        if product and product.group(1).lower() in {"may", "might", "has", "had", "was", "is", "could"}:
            product = None
    if not product:
        product = re.search(r"\b(?:discolou?red|darker(?:\s+in\s+color)?|damaged|leaking)\s+([A-Za-z][A-Za-z0-9 -]*?)\s+(?=\d+(?:\.\d+)?\s*(?:milligrams?|mg|grams?|g|mL|ml)\b)", message, re.I)
    if not product:
        product = re.search(r"\bof\s+([A-Za-z][A-Za-z0-9 -]*?)\s+(?=\d+(?:\.\d+)?\s*(?:milligrams?|mg|grams?|g|mL|ml)\b)", message, re.I)
    source = re.search(r"\bpurchased from\s+([A-Za-z][A-Za-z &'-]*?)(?=[.,!]|\s+while\b|$)", message, re.I)
    strength = re.search(r"strength\s+of\s+(\d+(?:\.\d+)?)\s*(milligrams?|mg)", message, re.I)
    if not strength:
        strength = re.search(r"\b(\d+(?:\.\d+)?)\s*(milligrams?|mg|grams?|g|mL|ml)\b", message, re.I)
    batch = re.search(r"batch(?: number)?(?:\s+on the package)?\s*(?:is|:)?\s*([\w-]+)", message, re.I)
    manufacturing = re.search(r"(?:manufacturing date|manufactured)\s+(?:on\s+)?([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4})", message, re.I)
    today = re.search(r"today is\s+([0-9]{1,2}[-/]\s*[0-9]{1,2}[-/]\s*[0-9]{4})", message, re.I)
    stated_date = re.search(r"(?:complaint date|received|reported)\s*(?:is|on|:)?\s*([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}|[0-9]{1,2}[-/]\s*[0-9]{1,2}[-/]\s*[0-9]{4})", message, re.I)

    if customer:
        complaint.customerName = customer.group(1).strip()
    if product:
        complaint.productName = re.sub(r"^product\s+", "", product.group(1).strip(), flags=re.I)
    if source:
        complaint.source = source.group(1).strip()
    if strength:
        unit = strength.group(2).lower()
        complaint.strength = f"{strength.group(1)} {'mg' if unit in ('mg', 'milligrams') else unit}"
    if batch:
        complaint.batchNumber = batch.group(1).strip()
    if manufacturing:
        complaint.manufacturingDate = _format_date(manufacturing.group(1))
        if re.search(r"expir\w*\s+after\s+one\s+year", message, re.I) and complaint.manufacturingDate:
            day, month, year = complaint.manufacturingDate.split("/")
            complaint.expiryDate = f"{day}/{month}/{int(year) + 1}"
    if today:
        complaint.complaintDate = _format_date(today.group(1).replace(" ", ""))
    elif stated_date:
        complaint.complaintDate = _format_date(stated_date.group(1).replace(" ", ""))

    defects = []
    if re.search(r"darker in color|discolou?red|discoloration", message, re.I):
        defects.append("discoloration")
    elif re.search(r"wrong color|color", message, re.I):
        defects.append("wrong color")
    if re.search(r"wrong size|size", message, re.I):
        defects.append("wrong size")
    if defects:
        complaint.complaintCategory = "Product Quality Issue"
        product = complaint.productName or "the reported product"
        batch = f" from batch {complaint.batchNumber}" if complaint.batchNumber else ""
        complaint.description = (
            f"Customer reported {', '.join(defects)} in {product}{batch}. "
            "The observation represents a potential product quality concern requiring investigation."
        )
    return complaint


def _infer_category(message: str) -> str:
    text = message.lower()
    if re.search(r"packag|seal|container|bottle|blister", text):
        return "Packaging Issue"
    if re.search(r"label|印|wrong name|incorrect information", text):
        return "Labeling Issue"
    if re.search(r"storage|temperature|heat|cold|humidity", text):
        return "Storage Issue"
    if re.search(r"delivery|shipping|distribution|transport", text):
        return "Distribution Issue"
    if re.search(r"service|staff|experience|support", text):
        return "Customer Experience Issue"
    if re.search(r"wrong color|discolou?red|wrong size|defect|damaged|broken", text):
        return "Product Quality Issue"
    return "Product Quality Issue"


def _infer_source(message: str) -> str:
    source = re.search(r"\bpurchased from\s+([A-Za-z][A-Za-z &'-]*?)(?=[.,!]|\s+while\b|$)", message, re.I)
    return source.group(1).strip() if source else ""


def has_explicit_complaint_date(message: str) -> bool:
    return bool(re.search(r"\b(?:complaint date|received|reported|today is)\b", message, re.I))


def extract_correction_patch(message: str) -> dict[str, str]:
    """Extract unambiguous corrections that should override model guesses."""
    patch: dict[str, str] = {}
    if re.search(r"\b(?:expiry|expiration|expiry)\s+date\s+(?:is|to|should be)\s+today(?:'s)?\s+date\b", message, re.I):
        patch["expiryDate"] = format_local_today()
    return patch


def extract_identity_patch(message: str) -> dict[str, str]:
    """Split explicit customer-name and source wording deterministically."""
    patch: dict[str, str] = {}
    customer = re.search(
        r"\b(?:customer\s+name|correct\s+name|name)\s*(?:is|:)?\s+(.+?)(?=\s+(?:and|from|via|through|at)\s+|[.,!]|$)",
        message,
        re.I,
    )
    if customer:
        patch["customerName"] = customer.group(1).strip()
        source = re.search(r"\bfrom\s+([^.,!]+)", message[customer.start():], re.I)
        if source:
            patch["source"] = source.group(1).strip()
        channel = re.search(r"\b(?:via|through)\s+(email|phone|telephone|portal|website|mail)\b", message[customer.start():], re.I)
        if channel:
            patch["source"] = channel.group(1).strip().title()
    else:
        channel = re.search(r"\b(?:complained|reported)\s+(?:via|through)\s+(email|phone|telephone|portal|website|mail)\b", message, re.I)
        if channel:
            patch["source"] = channel.group(1).strip().title()
    return patch


def _professional_description(complaint: ComplaintData, message: str) -> str:
    product = complaint.productName or "the reported product"
    strength = f" {complaint.strength}" if complaint.strength else ""
    batch = f" from batch {complaint.batchNumber}" if complaint.batchNumber else ""
    return (
        f"Customer reported a complaint concerning {product}{strength}{batch}. "
        "The available information has been documented for quality review and further investigation."
    )


def _assessment(complaint: ComplaintData, message: str) -> tuple[str, str, str]:
    text = message.lower()
    if re.search(r"critical|very high-risk|high-risk|serious", text):
        return (
            "Critical",
            "Escalate to QA Team and initiate immediate quality investigation.",
            "Critical risk indicated by the reported product defect and potential impact to product quality. Immediate containment and batch review are recommended."
        )
    if re.search(r"wrong color|darker in color|discolou?red|wrong size|defect|damaged", text):
        return (
            "Major",
            "Initiate Quality Investigation and request product samples.",
            "Potential product quality defect identified. The affected batch and product samples should be reviewed to determine scope and root cause."
        )
    if not any((complaint.productName, complaint.batchNumber, complaint.quantity)):
        return (
            "Minor",
            "Request additional complaint details before further assessment.",
            "Limited information was provided. The complaint should be clarified before determining broader product or batch impact."
        )
    return (
        "Major",
        "Monitor Complaint and perform batch review.",
        "Moderate risk pending confirmation of the complaint details and assessment of the affected product."
    )
