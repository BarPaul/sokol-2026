from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base


def _ensure_dir(url: str) -> str:
    if url.startswith("sqlite:///"):
        path = Path(url.removeprefix("sqlite:///"))
        path.parent.mkdir(parents=True, exist_ok=True)
    return url


engine = create_engine(
    _ensure_dir(settings.database_url),
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()