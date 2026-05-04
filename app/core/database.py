from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


def normalize_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


# Prefer Railway/host environment variable.
# Fallback points to the Neon production database shown during deployment setup.
DATABASE_URL = normalize_database_url(
    os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://neondb_owner:CHANGE_ME@ep-dawn-credit-am7vzvhd-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
    )
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
