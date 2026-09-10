"""Copy locally saved complaint records from SQLite into the configured database."""

import json
import sqlite3
import sys
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_settings
from app.database import Base
from app.models import ComplaintRecord


SQLITE_PATH = Path(__file__).resolve().parents[1] / "ccms.sqlite3"


def main() -> None:
    if not SQLITE_PATH.exists():
        print(f"No SQLite database found at {SQLITE_PATH}; nothing to migrate.")
        return

    sqlite = sqlite3.connect(SQLITE_PATH)
    sqlite.row_factory = sqlite3.Row
    rows = sqlite.execute(
        "SELECT id, complaint_json, assessment_json, original_text, source_file, mode, "
        "changed_fields_json, missing_fields_json, record_fingerprint, created_at "
        "FROM complaint_records ORDER BY id"
    ).fetchall()
    sqlite.close()

    target = create_engine(get_settings().database_url)
    Base.metadata.create_all(bind=target)
    inserted = 0
    skipped = 0

    with Session(target) as session:
        for row in rows:
            fingerprint = row["record_fingerprint"]
            existing = session.scalar(
                select(ComplaintRecord).where(
                    ComplaintRecord.record_fingerprint == fingerprint
                )
            ) if fingerprint else None
            if existing:
                skipped += 1
                continue

            record = ComplaintRecord(
                complaint_json=row["complaint_json"],
                assessment_json=row["assessment_json"],
                original_text=row["original_text"] or "",
                source_file=row["source_file"] or "",
                mode=row["mode"] or "demo",
                changed_fields_json=row["changed_fields_json"] or "[]",
                missing_fields_json=row["missing_fields_json"] or "[]",
                record_fingerprint=fingerprint,
            )
            if row["created_at"]:
                from datetime import datetime

                record.created_at = datetime.fromisoformat(row["created_at"])
            session.add(record)
            inserted += 1

        session.commit()

    print(json.dumps({"source_records": len(rows), "inserted": inserted, "skipped_duplicates": skipped}))


if __name__ == "__main__":
    main()
