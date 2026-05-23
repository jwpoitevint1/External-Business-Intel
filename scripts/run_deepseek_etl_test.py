import json
import os
from pathlib import Path

from app.agents.deepseek_etl_agent import DeepSeekETLAgent
from app.agents.qwen_analyst_agent import QwenAnalystAgent
from app.services.trend_ingestion import fetch_google_news, fetch_reddit

OUTPUT_DIR = Path("artifacts")
OUTPUT_DIR.mkdir(exist_ok=True)

query = os.getenv("TEST_QUERY", "social media marketing trends")
mode = os.getenv("TEST_MODE", "offline")

etl = DeepSeekETLAgent()
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
                "raw_text": n,
                "data_type": "public_content",
            }
        )

    for r in reddit:
        raw_records.append(
            {
                "source": "reddit",
                "source_url": "https://reddit.com",
                "raw_text": r,
                "data_type": "public_content",
            }
        )
else:
    raw_records = [
        {
            "source": "offline_fixture",
            "source_url": "https://example.local",
            "raw_text": "Small businesses are increasing spending on short-form video advertising and AI-assisted campaign management.",
            "data_type": "public_content",
        },
        {
            "source": "offline_fixture",
            "source_url": "https://example.local",
            "raw_text": "Marketing consultants report increased demand for social media analytics and local brand engagement.",
            "data_type": "public_content",
        },
    ]

normalized = [etl.normalize_public_signal(r) for r in raw_records]
normalized = etl.deduplicate(normalized)
validation = etl.validate(normalized)

for record in normalized:
    words = record["clean_text"].lower().split()
    record["keywords"] = list(set([w for w in words if len(w) > 4]))[:10]

analysis = qwen.analyze_trends(normalized)

payload = {
    "query": query,
    "mode": mode,
    "records_processed": len(normalized),
    "validation": validation,
    "analysis": analysis,
}

output_file = OUTPUT_DIR / "deepseek_etl_test_output.json"
output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

print(json.dumps(payload, indent=2))
