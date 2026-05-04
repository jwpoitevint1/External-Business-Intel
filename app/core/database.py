from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


def normalize_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


Base = declarative_base()
_engine = None
_SessionLocal = None


def get_database_url() -> str:
    raw_database_url = os.getenv("DATABASE_URL")
    if not raw_database_url:
        raise RuntimeError("DATABASE_URL environment variable is required.")
    return normalize_database_url(raw_database_url)


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(get_database_url(), pool_pre_ping=True)
    return _engine


def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db():
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
