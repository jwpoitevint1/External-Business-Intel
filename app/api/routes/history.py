from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.trend_report import TrendReport

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/history")
def trend_history(query: str | None = None, limit: int = 20, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 100))
    q = db.query(TrendReport).order_by(TrendReport.created_at.desc())
    if query:
        q = q.filter(TrendReport.query == query)

    records = q.limit(limit).all()
    return {
        "count": len(records),
        "items": [
            {
                "id": r.id,
                "query": r.query,
                "mode": r.mode,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "report": r.report,
            }
            for r in records
        ],
    }


@router.get("/latest")
def latest_trend_report(query: str | None = None, db: Session = Depends(get_db)):
    q = db.query(TrendReport).order_by(TrendReport.created_at.desc())
    if query:
        q = q.filter(TrendReport.query == query)

    r = q.first()
    if not r:
        return {"found": False, "item": None}

    return {
        "found": True,
        "item": {
            "id": r.id,
            "query": r.query,
            "mode": r.mode,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "report": r.report,
        },
    }
