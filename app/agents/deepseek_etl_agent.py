from datetime import datetime, timezone
from typing import Any, Dict, List

from app.core.cv11_policy import (
    DEEPSEEK_ETL_SCOPE,
    assert_action_allowed,
    assert_output_allowed,
    require_source_binding,
)


class DeepSeekETLAgent:
    """DeepSeek is hard-scoped to ETL only.

    It may extract, normalize, deduplicate, validate, and load source-bound records.
    It must not analyze, recommend, report, interpret market meaning, or mutate protected source data.
    """

    name = "deepseek_etl"

    def normalize_public_signal(self, raw_record: Dict[str, Any]) -> Dict[str, Any]:
        assert_action_allowed(DEEPSEEK_ETL_SCOPE, "normalize")
        assert_output_allowed(DEEPSEEK_ETL_SCOPE, "normalized_record")

        normalized = {
            "source": raw_record.get("source"),
            "source_url": raw_record.get("source_url"),
            "raw_text": raw_record.get("raw_text", ""),
            "clean_text": " ".join(str(raw_record.get("raw_text", "")).split()),
            "observed_at": raw_record.get("observed_at") or datetime.now(timezone.utc).isoformat(),
            "keywords": raw_record.get("keywords", []),
            "metadata": raw_record.get("metadata", {}),
        }

        require_source_binding([normalized])
        return normalized

    def deduplicate(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        assert_action_allowed(DEEPSEEK_ETL_SCOPE, "deduplicate")
        seen = set()
        output = []

        for record in records:
            fingerprint = (
                record.get("source"),
                record.get("source_url"),
                record.get("clean_text") or record.get("raw_text"),
            )
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            output.append(record)

        return output

    def validate(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        assert_action_allowed(DEEPSEEK_ETL_SCOPE, "validate")
        assert_output_allowed(DEEPSEEK_ETL_SCOPE, "validation_report")
        require_source_binding(records)

        return {
            "agent": self.name,
            "valid": True,
            "record_count": len(records),
            "policy": "CV 1.1 source-bound ETL validation passed",
        }
