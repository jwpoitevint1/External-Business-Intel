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
    # 1. Ingest public data only
    news = fetch_google_news(query)
    reddit = fetch_reddit(query)

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

    # Enforce public-domain-only policy
    validate_public_records(raw_records)

    # 2. DeepSeek ETL
    normalized = [etl_agent.normalize_public_signal(r) for r in raw_records]
    normalized = etl_agent.deduplicate(normalized)
    validation = etl_agent.validate(normalized)

    # Deterministic keyword extraction
    for record in normalized:
        words = record["clean_text"].lower().split()
        record["keywords"] = list(set([w for w in words if len(w) > 4]))[:10]

    # 3. Qwen Analysis
    report = analyst.analyze_trends(normalized)

    # 4. Persist report
    db_record = TrendReport(
        query=query,
        report=report,
    )
    db.add(db_record)
    db.commit()

    return {
        "query": query,
        "mode": "on_demand",
        "records_processed": len(normalized),
        "validation": validation,
        "analysis": report,
        "stored": True,
    }
