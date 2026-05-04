import json
import os
from typing import Any, Dict, List

from openai import OpenAI

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
    model = os.getenv("QWEN_MODEL", "Qwen/Qwen3.6-35B-A3B:featherless-ai")
    base_url = os.getenv("QWEN_BASE_URL", "https://router.huggingface.co/v1")

    def analyze_trends(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        assert_action_allowed(QWEN_ANALYST_SCOPE, "analyze")
        assert_output_allowed(QWEN_ANALYST_SCOPE, "trend_analysis")

        if os.getenv("HF_TOKEN"):
            return self._analyze_with_qwen(records)

        return self._deterministic_fallback(records)

    def _analyze_with_qwen(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        client = OpenAI(
            base_url=self.base_url,
            api_key=os.environ["HF_TOKEN"],
        )

        evidence_payload = []
        for idx, record in enumerate(records[:30], start=1):
            evidence_payload.append(
                {
                    "id": idx,
                    "source": record.get("source"),
                    "source_url": record.get("source_url"),
                    "excerpt": (record.get("clean_text") or record.get("raw_text", ""))[:500],
                    "keywords": record.get("keywords", []),
                }
            )

        prompt = f"""
You are Qwen, a tactical business intelligence analyst for a private external business intelligence system.

Scope:
- Analyze only the provided public-domain evidence.
- Do not invent facts, sources, statistics, or events.
- Do not mutate, rewrite, or normalize source records.
- Treat opinions as language signals, not verified facts.
- Focus on marketing, advertising, consulting, mass media, and small-business implications.
- If evidence is weak, label confidence as low.

Return JSON only with this exact structure:
{{
  "agent": "qwen_analyst",
  "type": "monitoring_report",
  "trends": [
    {{
      "trend": "short trend name",
      "strength": "low|medium|high",
      "confidence": "low|medium|high",
      "score": 0,
      "evidence": [
        {{"source": "", "source_url": "", "excerpt": ""}}
      ],
      "implication": "what this means for business/marketing",
      "recommended_action": "tactical action"
    }}
  ]
}}

Evidence records:
{json.dumps(evidence_payload, ensure_ascii=False)}
"""

        completion = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        content = completion.choices[0].message.content
        report = self._parse_json_report(content)
        return self._validate_report(report)

    def _parse_json_report(self, content: str) -> Dict[str, Any]:
        try:
            return json.loads(content)
        except Exception:
            start = content.find("{")
            end = content.rfind("}")
            if start >= 0 and end > start:
                return json.loads(content[start : end + 1])
            raise ValueError("Qwen returned non-JSON output")

    def _validate_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        report.setdefault("agent", self.name)
        report.setdefault("type", "monitoring_report")
        report.setdefault("trends", [])

        for claim in report.get("trends", []):
            refuse_if_unsourced_claim(claim)
            claim.setdefault("confidence", "low")
            claim.setdefault("score", 0)

        return report

    def _deterministic_fallback(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        freq: Dict[str, int] = {}
        for r in records:
            for k in r.get("keywords", []):
                freq[k] = freq.get(k, 0) + 1

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
                "confidence": "low",
                "score": min(100, count * 10),
                "evidence": evidence,
                "implication": self._implication(term),
                "recommended_action": self._recommendation(term),
            }

            refuse_if_unsourced_claim(claim)
            trends.append(claim)

        return {
            "agent": self.name,
            "type": "monitoring_report",
            "mode": "deterministic_fallback_no_hf_token",
            "trends": trends,
        }

    def _strength_from_count(self, count: int) -> str:
        if count >= 10:
            return "high"
        if count >= 5:
            return "medium"
        return "low"

    def _implication(self, term: str) -> str:
        return f"Increased discussion around '{term}' indicates demand or friction in this area for small businesses."

    def _recommendation(self, term: str) -> str:
        return (
            f"Position services that address '{term}' in outreach messaging and audits. "
            f"Test a 14-day sprint offering tied to this topic with measurable indicator codes."
        )
