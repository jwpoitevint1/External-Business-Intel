from fastapi import APIRouter
from app.services.trend_ingestion import fetch_google_news, fetch_reddit

router = APIRouter(prefix="/trends", tags=["trends"])

@router.get("/scan")
def scan_trends(query: str):
    news = fetch_google_news(query)
    reddit = fetch_reddit(query)

    return {
        "query": query,
        "news": news,
        "reddit": reddit
    }
