from fastapi import APIRouter

from app.services.trend_ingestion import fetch_google_news, fetch_reddit
from app.agents.deepseek_etl_agent import DeepSeekETLAgent
from app.agents.qwen_analyst_agent import QwenAnalystAgent

router = APIRouter(prefix="/trends", tags=["trends"])

etl_agent = DeepSeekETLAgent()
analyst = QwenAnalystAgent()


@router.get("/scan")
def scan_trends(query: str):
    # 1. Ingest public data
    news = fetch_google_news(query)
    reddit = fetch_reddit(query)

    raw_records = []

    for n in news:
        raw_records.append({
            "source": "google_news",
            "source_url": "https://news.google.com",
            "raw_text": n,
        })

    for r in reddit:
        raw_records.append({
            "source": "reddit",
            "source_url": "https://reddit.com",
            "raw_text": r,
        })

    # 2. DeepSeek ETL (strict CV 1.1)
    normalized = [etl_agent.normalize_public_signal(r) for r in raw_records]
    normalized = etl_agent.deduplicate(normalized)
    validation = etl_agent.validate(normalized)

    # Deterministic keyword extraction (no hallucination)
    for record in normalized:
        words = record["clean_text"].lower().split()
        record["keywords"] = list(set([w for w in words if len(w) > 4]))[:10]

    # 3. Qwen Tactical Analysis
    report = analyst.analyze_trends(normalized)

    return {
        "query": query,
        "mode": "on_demand",
        "records_processed": len(normalized),
        "validation": validation,
        "analysis": report,
    }
