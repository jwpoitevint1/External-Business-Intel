from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.services.trend_ingestion import fetch_google_news, fetch_reddit
from app.agents.deepseek_etl_agent import DeepSeekETLAgent
from app.agents.qwen_analyst_agent import QwenAnalystAgent
from app.core.public_domain_policy import validate_public_records
from app.core.database import get_db
from app.models.trend_report import TrendReport

router = APIRouter(prefix="/trends", tags=["trends"])

etl_agent = DeepSeekETLAgent()
analyst = QwenAnalystAgent()


@router.get("/scan")
def scan_trends(query: str, db: Session = Depends(get_db)):
    debug_steps = []

    try:
        news = fetch_google_news(query)
        reddit = fetch_reddit(query)
        debug_steps.append({"step": "ingestion", "status": "ok", "news_count": len(news), "reddit_count": len(reddit)})
    except Exception as exc:
        return {"status": "error", "failed_step": "ingestion", "error_type": type(exc).__name__, "error": str(exc)}

    try:
        raw_records = []

        for n in news:
            raw_records.append({
                "source": "google_news",
                "source_url": "https://news.google.com",
                "raw_text": n,
                "data_type": "public_content",
            })

        for r in reddit:
            raw_records.append({
                "source": "reddit",
                "source_url": "https://reddit.com",
                "raw_text": r,
                "data_type": "public_content",
            })

        if not raw_records:
            raw_records.append({
                "source": "system",
                "source_url": "https://web-production-d6ffa.up.railway.app",
                "raw_text": f"No public records returned for query: {query}",
                "data_type": "public_content",
            })

        validate_public_records(raw_records)
        debug_steps.append({"step": "public_policy", "status": "ok", "raw_count": len(raw_records)})
    except Exception as exc:
        return {"status": "error", "failed_step": "public_policy", "error_type": type(exc).__name__, "error": str(exc), "debug_steps": debug_steps}

    try:
        normalized = [etl_agent.normalize_public_signal(r) for r in raw_records]
        normalized = etl_agent.deduplicate(normalized)
        validation = etl_agent.validate(normalized)

        for record in normalized:
            words = record["clean_text"].lower().split()
            record["keywords"] = list(set([w for w in words if len(w) > 4]))[:10]

        debug_steps.append({"step": "etl", "status": "ok", "normalized_count": len(normalized)})
    except Exception as exc:
        return {"status": "error", "failed_step": "etl", "error_type": type(exc).__name__, "error": str(exc), "debug_steps": debug_steps}

    try:
        report = analyst.analyze_trends(normalized)
        debug_steps.append({"step": "analysis", "status": "ok", "trend_count": len(report.get("trends", []))})
    except Exception as exc:
        return {"status": "error", "failed_step": "analysis", "error_type": type(exc).__name__, "error": str(exc), "debug_steps": debug_steps}

    try:
        db_record = TrendReport(query=query, report=report)
        db.add(db_record)
        db.commit()
        debug_steps.append({"step": "storage", "status": "ok"})
    except Exception as exc:
        db.rollback()
        return {"status": "error", "failed_step": "storage", "error_type": type(exc).__name__, "error": str(exc), "debug_steps": debug_steps}

    return {
        "status": "ok",
        "query": query,
        "mode": "on_demand",
        "records_processed": len(normalized),
        "validation": validation,
        "analysis": report,
        "stored": True,
        "debug_steps": debug_steps,
    }
