from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class ComplaintRecord(Base):
    __tablename__ = "complaint_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    complaint_json: Mapped[str] = mapped_column(Text, nullable=False)
    assessment_json: Mapped[str] = mapped_column(Text, nullable=False)
    original_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    source_file: Mapped[str] = mapped_column(Text, default="", nullable=False)
    mode: Mapped[str] = mapped_column(Text, default="demo", nullable=False)
    changed_fields_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    missing_fields_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    record_fingerprint: Mapped[str] = mapped_column(String(64), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
