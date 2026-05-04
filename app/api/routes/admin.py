from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.init_db import init_db

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/smoke")
def smoke_test(db: Session = Depends(get_db)):
    checks = []

    checks.append({"name": "api_boot", "status": "ok"})

    db_result = db.execute(text("SELECT 1 AS ok")).mappings().first()
    checks.append({"name": "database_connection", "status": "ok", "result": dict(db_result) if db_result else None})

    init_db()
    checks.append({"name": "database_tables", "status": "ok"})

    return {
        "system": "external-business-intel",
        "smoke_status": "ok",
        "checks": checks,
    }
