from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


def _engine_options(database_url: str) -> dict:
    return {"connect_args": {"check_same_thread": False}} if database_url.startswith("sqlite") else {}


settings = get_settings()
engine = create_engine(settings.database_url, **_engine_options(settings.database_url))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def create_tables() -> None:
    from .models import ComplaintRecord

    Base.metadata.create_all(bind=engine)
    existing_columns = {column["name"] for column in inspect(engine).get_columns("complaint_records")}
    migrations = {
        "changed_fields_json": "ALTER TABLE complaint_records ADD COLUMN changed_fields_json TEXT NOT NULL DEFAULT '[]'",
        "missing_fields_json": "ALTER TABLE complaint_records ADD COLUMN missing_fields_json TEXT NOT NULL DEFAULT '[]'",
        "record_fingerprint": "ALTER TABLE complaint_records ADD COLUMN record_fingerprint VARCHAR(64)",
    }
    with engine.begin() as connection:
        for column, statement in migrations.items():
            if column not in existing_columns:
                connection.execute(text(statement))
