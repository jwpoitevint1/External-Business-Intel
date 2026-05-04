from typing import Any, Dict, List

from app.core.cv11_policy import (
    QWEN_ANALYST_SCOPE,
    assert_action_allowed,
    assert_output_allowed,
    refuse_if_unsourced_claim,
)


class QwenAnalystAgent:
    """Qwen is a tactical analyst.

    It analyzes normalized, source-bound records and produces evidence-backed
    trend assessments and actionable recommendations for SMB marketing.
    It must not perform ETL or mutate source data.
    """

    name = "qwen_analyst"

    def analyze_trends(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        assert_action_allowed(QWEN_ANALYST_SCOPE, "analyze")
        assert_output_allowed(QWEN_ANALYST_SCOPE, "trend_analysis")

        # Simple deterministic clustering by keyword frequency (placeholder for model call)
        freq: Dict[str, int] = {}
        for r in records:
            for k in r.get("keywords", []):
                freq[k] = freq.get(k, 0) + 1

        # Select top keywords as trends
        sorted_terms = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]

        trends = []
        for term, count in sorted_terms:
            evidence = [
                {
                    "source": r.get("source"),
                    "source_url": r.get("source_url"),
                    "excerpt": (r.get("clean_text") or r.get("raw_text", ""))[:200],
                }
                for r in records
                if term in r.get("keywords", [])
            ][:5]

            claim = {
                "trend": term,
                "strength": self._strength_from_count(count),
                "evidence": evidence,
                "implication": self._implication(term),
                "recommended_action": self._recommendation(term),
            }

            # CV 1.1: refuse if no evidence
            refuse_if_unsourced_claim(claim)
            trends.append(claim)

        return {
            "agent": self.name,
            "type": "monitoring_report",
            "trends": trends,
        }

    def _strength_from_count(self, count: int) -> str:
        if count >= 10:
            return "high"
        if count >= 5:
            return "medium"
        return "low"

    def _implication(self, term: str) -> str:
        # Tactical, but still generic and safe; replace with model-backed interpretation later
        return f"Increased discussion around '{term}' indicates demand or friction in this area for small businesses."

    def _recommendation(self, term: str) -> str:
        # Tactical recommendation pattern tied to outreach/ops model
        return (
            f"Position services that address '{term}' in outreach messaging and audits. "
            f"Test a 14-day sprint offering tied to this topic with measurable indicator codes."
        )
