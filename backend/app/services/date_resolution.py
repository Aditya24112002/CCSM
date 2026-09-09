"""Application-local natural-language date resolution."""

import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from ..config import get_settings


WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}


def local_today() -> date:
    return datetime.now(ZoneInfo(get_settings().app_timezone)).date()


def format_local_today() -> str:
    return local_today().strftime("%d/%m/%Y")


def resolve_date_expression(expression: str, reference: date | None = None) -> str:
    """Resolve a relative date expression to DD/MM/YYYY, or return empty."""
    current = reference or local_today()
    value = expression.lower().strip().replace("’", "'")
    value = re.sub(r"\s+", " ", value)

    if re.search(r"\bnew year's day\b|\bnew year\b", value):
        year_match = re.search(r"\b(20\d{2})\b", value)
        return date(int(year_match.group(1)) if year_match else current.year, 1, 1).strftime("%d/%m/%Y")
    if value in {"today", "today's date"}:
        return current.strftime("%d/%m/%Y")
    if value in {"yesterday", "yesterday's date"}:
        return (current - timedelta(days=1)).strftime("%d/%m/%Y")
    if value in {"tomorrow", "tomorrow's date"}:
        return (current + timedelta(days=1)).strftime("%d/%m/%Y")

    duration = re.fullmatch(r"(?:after|in)\s+(\d+)\s+days?(?:\s+from\s+today)?", value)
    if duration:
        return (current + timedelta(days=int(duration.group(1)))).strftime("%d/%m/%Y")

    weekday = re.fullmatch(r"(?:the\s+)?next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", value)
    if weekday:
        target = WEEKDAYS[weekday.group(1)]
        days_ahead = (target - current.weekday()) % 7 or 7
        return (current + timedelta(days=days_ahead)).strftime("%d/%m/%Y")
    return ""


def extract_relative_date_patch(message: str) -> dict[str, str]:
    """Resolve relative dates tied to complaint form fields."""
    patterns = [
        ("expiryDate", r"(?:expiry|expiration|expedition)\s+date\s+(?:is|was|will be|to|on)\s+([^.,!]+)"),
        ("manufacturingDate", r"(?:manufacturing|manufacture)\s+date\s+(?:is|was|will be|to|on)\s+([^.,!]+)"),
        ("manufacturingDate", r"manufactured\s+(?:on|in)\s+([^.,!]+)"),
        ("complaintDate", r"complaint\s+date\s+(?:is|was|will be|to|on)\s+([^.,!]+)"),
    ]
    patch: dict[str, str] = {}
    for field, pattern in patterns:
        match = re.search(pattern, message, re.I)
        if not match:
            continue
        expression = match.group(1).strip()
        resolved = resolve_date_expression(expression)
        if not resolved:
            # Also accept "2024 New Year" where the year precedes the phrase.
            new_year = re.search(r"\b(20\d{2})\s+new year(?:'s day)?\b", expression, re.I)
            if new_year:
                resolved = date(int(new_year.group(1)), 1, 1).strftime("%d/%m/%Y")
        if resolved:
            patch[field] = resolved
    return patch
