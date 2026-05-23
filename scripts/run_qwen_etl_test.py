import json
import os
from datetime import datetime, timezone
from pathlib import Path

from app.agents.qwen_analyst_agent import QwenAnalystAgent
from app.core.public_domain_policy import validate_public_records
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
            "source_url": "https://news.google.com",
            "raw_text": "Small businesses are increasing spending on short-form video advertising and AI-assisted campaign management.",
            "data_type": "public_content",
        },
        {
            "source": "offline_fixture",
            "source_url": "https://reddit.com",
            "raw_text": "Marketing consultants report increased demand for social media analytics and local brand engagement.",
            "data_type": "public_content",
        },
    ]

validate_public_records(raw_records)

normalized_records = []
for record in raw_records:
    clean_text = " ".join(str(record.get("raw_text", "")).split())
    words = clean_text.lower().split()
    normalized_records.append(
        {
            "source": record.get("source"),
            "source_url": record.get("source_url"),
            "raw_text": record.get("raw_text", ""),
            "clean_text": clean_text,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "keywords": list(dict.fromkeys([w.strip(".,!?;:()[]{}\"'") for w in words if len(w) > 4]))[:10],
            "metadata": {"test_mode": mode, "query": query},
        }
    )

seen = set()
deduped_records = []
for record in normalized_records:
    fingerprint = (record.get("source"), record.get("source_url"), record.get("clean_text"))
    if fingerprint in seen:
        continue
    seen.add(fingerprint)
    deduped_records.append(record)

analysis = qwen.analyze_trends(deduped_records)

payload = {
    "query": query,
    "mode": mode,
    "records_processed": len(deduped_records),
    "preprocessing": {
        "agent": "deterministic_preprocessor",
        "policy": "public-domain validation + normalization + dedupe before Qwen analysis",
        "valid": True,
    },
    "analysis": analysis,
}

output_file = OUTPUT_DIR / "qwen_analysis_test_output.json"
output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

print(json.dumps(payload, indent=2))
