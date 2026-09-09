import logging

from ..config import get_settings
from ..schemas import IntakeRequest, IntakeResponse
from .demo_extractor import extract_demo
from .langgraph_extractor import extract_with_langgraph


logger = logging.getLogger(__name__)


def extract_complaint(request: IntakeRequest) -> IntakeResponse:
    settings = get_settings()
    if not settings.groq_api_key:
        return extract_demo(request)

    try:
        return extract_with_langgraph(request)
    except Exception:
        # Keep local development usable if the model, key, or network is unavailable.
        logger.exception("LangGraph/Groq extraction failed; using deterministic fallback")
        return extract_demo(request)
