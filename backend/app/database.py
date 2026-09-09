from sqlalchemy import create_engine
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
