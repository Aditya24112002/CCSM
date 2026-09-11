import re
from typing import TypedDict

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from ..config import get_settings
from ..schemas import ComplaintData, IntakeRequest, IntakeResponse, RiskAssessment
from .date_resolution import extract_relative_date_patch, format_local_today
from .demo_extractor import (
    REQUIRED_FIELDS,
    extract_correction_patch,
    extract_document_patch,
    extract_identity_patch,
    has_explicit_complaint_date,
)
from .extraction_examples import EXTRACTION_EXAMPLES


class ExtractedComplaint(BaseModel):
    source: str | None = None
    customerName: str | None = None
    productName: str | None = None
    strength: str | None = None
    batchNumber: str | None = None
    manufacturingDate: str | None = Field(default=None, description="Normalize to DD/MM/YYYY")
    expiryDate: str | None = Field(default=None, description="Normalize to DD/MM/YYYY")
    quantity: str | None = None
    complaintCategory: str | None = None
    complaintDate: str | None = Field(default=None, description="Normalize to DD/MM/YYYY")
    description: str | None = None
    severity: str | None = None
    suggestedNextAction: str | None = None
    initialRiskAssessment: str | None = None


class ComplaintState(TypedDict):
    request: IntakeRequest
    first_pass: ExtractedComplaint | None
    second_pass: ExtractedComplaint | None
    response: IntakeResponse | None


def _get_structured_llm():
    settings = get_settings()
    llm = ChatGroq(model=settings.groq_model, temperature=0, api_key=settings.groq_api_key)
    # gpt-oss-20b returns valid JSON directly, but may not emit a tool call.
    # JSON mode avoids the tool-choice failure and is parsed into the Pydantic schema.
    return llm.with_structured_output(ExtractedComplaint, method="json_mode")


def _invoke_pass(structured_llm, request: IntakeRequest, prompt: str) -> ExtractedComplaint:
    existing = request.existingComplaint or ComplaintData()
    result = structured_llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"Existing complaint:\n{existing.model_dump_json()}\n\nNew complaint or correction:\n{request.message}"),
    ])
    return result


def _extract_pass_one(state: ComplaintState) -> ComplaintState:
    structured_llm = _get_structured_llm()
    result = _invoke_pass(structured_llm, state["request"], (
        "You are pass 1 of a pharmaceutical quality complaint intake workflow. "
        "Extract every explicit fact supported by the complaint into the structured schema. "
        "Preserve existing values unless the user clearly corrects them. Normalize dates to DD/MM/YYYY. "
        "A first-time complaint can contain the word batch; do not treat it as an edit. "
        "If expiry is expressed as after/in a number of days, calculate it from the application-local current date. "
        "If expiry is expressed relative to manufacturing, calculate the resulting date. "
        "Generate a professional complaint category, concise business-ready description, severity, suggested next action, "
        "and initial risk assessment. Product name must exclude dosage strength. Always provide these assessment outputs.\n\n"
        "Return exactly one JSON object using the structured schema; do not return Markdown or explanatory text.\n\n"
        f"{EXTRACTION_EXAMPLES}\n\nThe application timezone is Asia/Kolkata and the current local date is {format_local_today()}. Resolve today, yesterday, tomorrow, next weekdays, and New Year dates using that timezone. Never output the literal CURRENT_DATE_DD/MM/YYYY placeholder."
    ))
    return {**state, "first_pass": result}


def _extract_pass_two(state: ComplaintState) -> ComplaintState:
    request = state["request"]
    existing = request.existingComplaint or ComplaintData()
    first = state["first_pass"] or ExtractedComplaint()
    known = {**existing.model_dump(), **first.model_dump(exclude_none=True)}
    missing = [field for field in REQUIRED_FIELDS if not known.get(field)]
    structured_llm = _get_structured_llm()
    result = _invoke_pass(structured_llm, request, (
        "You are pass 2 of a pharmaceutical quality complaint intake workflow. "
        f"Re-analyze the complaint specifically for missed fields: {', '.join(missing) or 'none'}. "
        "Return explicit facts that pass 1 missed, and make only reasonable, high-confidence inferences "
        "such as a relative expiry date or a clearly stated complaint date. Resolve 'after N days' from the application-local current date. Leave low-confidence fields null. "
        "Normalize dates to DD/MM/YYYY, preserve existing values, and do not guess names, products, batches, "
        "quantities, or dates. Always provide a professional category and assessment outputs."
        " Return exactly one JSON object using the structured schema; do not return Markdown or explanatory text."
        f"\n\n{EXTRACTION_EXAMPLES}\n\nThe application timezone is Asia/Kolkata and the current local date is {format_local_today()}. Resolve today, yesterday, tomorrow, next weekdays, and New Year dates using that timezone. Never output the literal CURRENT_DATE_DD/MM/YYYY placeholder."
    ))
    return {**state, "second_pass": result}


def _finalize_node(state: ComplaintState) -> ComplaintState:
    request = state["request"]
    existing = request.existingComplaint or ComplaintData()
    first = state["first_pass"] or ExtractedComplaint()
    second = state["second_pass"] or ExtractedComplaint()
    extracted = {**first.model_dump(exclude_none=True), **second.model_dump(exclude_none=True)}
    severity = extracted.pop("severity", None)
    risk_action = extracted.pop("suggestedNextAction", None)
    risk_summary = extracted.pop("initialRiskAssessment", None)
    merged = existing.model_copy(update=extracted)
    merged = merged.model_copy(update=extract_correction_patch(request.message))
    merged = merged.model_copy(update=extract_relative_date_patch(request.message))
    merged = merged.model_copy(update=extract_document_patch(request.message))
    merged = merged.model_copy(update=extract_identity_patch(request.message))
    if not existing.complaintDate and not has_explicit_complaint_date(request.message):
        merged.complaintDate = format_local_today()
    if not merged.source:
        source_match = re.search(r"\bpurchased from\s+([A-Za-z][A-Za-z &'-]*?)(?=[.,!]|\s+while\b|$)", request.message, re.I)
        if source_match:
            merged.source = source_match.group(1).strip()
    if not merged.complaintCategory:
        merged.complaintCategory = "Product Quality Issue"
    if not merged.description:
        merged.description = "Customer complaint documented for quality review and further investigation."
    severity = severity or "Major"
    has_substantive_context = bool(
        existing.productName
        or existing.batchNumber
        or extracted.get("productName")
        or extracted.get("batchNumber")
        or re.search(r"quality|defect|discolou?red|darker|damaged|wrong|leak|broken|seal", request.message, re.I)
    )
    if not has_substantive_context and severity in {"Major", "High", "Critical"}:
        severity = "Minor"
        risk_action = "Request additional complaint details before further assessment."
        risk_summary = "Limited information was provided. The complaint should be clarified before determining broader product or batch impact."
    changed_fields = [field for field in ComplaintData.model_fields if getattr(merged, field) != getattr(existing, field)]
    return {
        **state,
        "response": IntakeResponse(
            complaint=merged,
            riskAssessment=RiskAssessment(
                severity=severity,
                suggestedNextAction=risk_action or "Initiate Quality Investigation and perform batch review.",
                initialRiskAssessment=risk_summary or "Moderate risk pending review of the complaint and affected product.",
            ),
            changedFields=changed_fields,
            missingFields=[field for field in REQUIRED_FIELDS if not getattr(merged, field)],
            sourceFile=request.sourceFile,
            mode="langgraph-groq",
        ),
    }


def build_extraction_graph():
    graph = StateGraph(ComplaintState)
    graph.add_node("extract_pass_one", _extract_pass_one)
    graph.add_node("extract_pass_two", _extract_pass_two)
    graph.add_node("finalize", _finalize_node)
    graph.add_edge(START, "extract_pass_one")
    graph.add_edge("extract_pass_one", "extract_pass_two")
    graph.add_edge("extract_pass_two", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()


def extract_with_langgraph(request: IntakeRequest) -> IntakeResponse:
    result = build_extraction_graph().invoke({"request": request, "first_pass": None, "second_pass": None, "response": None})
    return result["response"]
