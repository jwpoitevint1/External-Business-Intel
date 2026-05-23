import json
import os
from pathlib import Path

from app.agents.qwen_analyst_agent import QwenAnalystAgent
from app.services.trend_ingestion import fetch_google_news, fetch_reddit

OUTPUT_DIR = Path("artifacts")
OUTPUT_DIR.mkdir(exist_ok=True)

query = os.getenv("TEST_QUERY", "social media marketing trends")
mode = os.getenv("TEST_MODE", "offline")

qwen = QwenAnalystAgent()

raw_records = []

if mode == "live":
    news = fetch_google_news(query)
    reddit = fetch_reddit(query)

    for n in news:
        raw_records.append(
            {
                "source": "google_news",
                "source_url": "https://news.google.com",
                "clean_text": n,
                "keywords": [w for w in n.lower().split() if len(w) > 4][:10],
            }
        )

    for r in reddit:
        raw_records.append(
            {
                "source": "reddit",
                "source_url": "https://reddit.com",
                "clean_text": r,
                "keywords": [w for w in r.lower().split() if len(w) > 4][:10],
            }
        )
else:
    raw_records = [
        {
            "source": "offline_fixture",
            "source_url": "https://example.local",
            "clean_text": "Small businesses are increasing spending on short-form video advertising and AI-assisted campaign management.",
            "keywords": ["businesses", "spending", "advertising", "campaign", "management"],
        },
        {
            "source": "offline_fixture",
            "source_url": "https://example.local",
            "clean_text": "Marketing consultants report increased demand for social media analytics and local brand engagement.",
            "keywords": ["marketing", "consultants", "analytics", "social", "engagement"],
        },
    ]

analysis = qwen.analyze_trends(raw_records)

payload = {
    "query": query,
    "mode": mode,
    "records_processed": len(raw_records),
    "analysis": analysis,
}

output_file = OUTPUT_DIR / "qwen_etl_test_output.json"
output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

print(json.dumps(payload, indent=2))
