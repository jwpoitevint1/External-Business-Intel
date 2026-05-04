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
    name = "qwen_analyst"
    default_model = "Qwen/Qwen3.6-35B-A3B:featherless-ai"
    default_base_url = "https://router.huggingface.co/v1"

    def __init__(self):
        self.model = os.getenv("QWEN_MODEL", self.default_model)
        self.base_url = os.getenv("QWEN_BASE_URL", self.default_base_url)
        self.hf_token = os.getenv("HF_TOKEN")

    def analyze_trends(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        assert_action_allowed(QWEN_ANALYST_SCOPE, "analyze")
        assert_output_allowed(QWEN_ANALYST_SCOPE, "trend_analysis")

        if not records:
            return self._empty_report("No normalized public-domain records were provided.")

        if self.hf_token:
            try:
                return self._analyze_with_qwen(records)
            except Exception as exc:
                fallback = self._deterministic_fallback(records)
                fallback["mode"] = "deterministic_fallback_qwen_error"
                fallback["qwen_error"] = f"{type(exc).__name__}: {str(exc)}"
                return fallback

        return self._deterministic_fallback(records)

    def _analyze_with_qwen(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        client = OpenAI(base_url=self.base_url, api_key=self.hf_token)
        evidence_payload = self._build_evidence_payload(records)

        completion = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": self._user_prompt(evidence_payload)},
            ],
            temperature=0.2,
            max_tokens=1800,
        )

        content = completion.choices[0].message.content or ""
        report = self._parse_json_report(content)
        return self._validate_report(report, records)

    def _system_prompt(self) -> str:
        return (
            "You are Qwen, a tactical business intelligence analyst for a private external business intelligence system. "
            "You analyze only provided public-domain evidence. You never invent facts, sources, statistics, events, or quotes. "
            "You do not mutate, rewrite, normalize, extract, load, or delete source records. "
            "Treat opinions as language signals, not verified facts. "
            "Focus on marketing, advertising, consulting, mass media, social media, and small-business implications. "
            "If evidence is weak, confidence must be low. Return JSON only."
        )

    def _user_prompt(self, evidence_payload: List[Dict[str, Any]]) -> str:
        return f"""
Analyze the evidence records and return the strongest business-relevant trends only.

Rules:
- Use only evidence records provided below.
- Every trend must include at least one evidence item copied from the supplied records.
- Do not claim that an opinion is true; describe it as a signal or pattern.
- Prefer actionable implications for small businesses, marketing operations, advertising, consulting, and mass media.
- Avoid generic filler.
- Score: 0-100 based on evidence strength, repetition, and business relevance.
- Confidence: low, medium, or high.

Return JSON only in this exact structure:
{{
  "agent": "qwen_analyst",
  "type": "monitoring_report",
  "mode": "qwen_hf_router",
  "trends": [
    {{
      "trend": "short trend name",
      "strength": "low|medium|high",
      "confidence": "low|medium|high",
      "score": 0,
      "evidence": [
        {{"source": "", "source_url": "", "excerpt": ""}}
      ],
      "implication": "business meaning",
      "recommended_action": "tactical next action"
    }}
  ]
}}

Evidence records:
{json.dumps(evidence_payload, ensure_ascii=False)}
"""

    def _build_evidence_payload(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        payload = []
        for idx, record in enumerate(records[:40], start=1):
            excerpt = (record.get("clean_text") or record.get("raw_text") or "")[:600]
            if not excerpt:
                continue
            payload.append(
                {
                    "id": idx,
                    "source": record.get("source", "unknown"),
                    "source_url": record.get("source_url", ""),
                    "excerpt": excerpt,
                    "keywords": record.get("keywords", []),
                }
            )
        return payload

    def _parse_json_report(self, content: str) -> Dict[str, Any]:
        content = content.strip()
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(content)
        except Exception:
            start = content.find("{")
            end = content.rfind("}")
            if start >= 0 and end > start:
                return json.loads(content[start : end + 1])
            raise ValueError("Qwen returned non-JSON output")

    def _validate_report(self, report: Dict[str, Any], records: List[Dict[str, Any]]) -> Dict[str, Any]:
        report.setdefault("agent", self.name)
        report.setdefault("type", "monitoring_report")
        report.setdefault("mode", "qwen_hf_router")
        report.setdefault("trends", [])

        cleaned_trends = []
        for claim in report.get("trends", [])[:8]:
            if not isinstance(claim, dict):
                continue
            claim.setdefault("trend", "Unlabeled trend")
            claim["strength"] = self._normalize_level(claim.get("strength"))
            claim["confidence"] = self._normalize_level(claim.get("confidence"))
            claim["score"] = self._normalize_score(claim.get("score"))
            claim.setdefault("implication", "No implication provided.")
            claim.setdefault("recommended_action", "Review evidence before acting.")
            claim["evidence"] = self._clean_evidence(claim.get("evidence", []), records)
            refuse_if_unsourced_claim(claim)
            cleaned_trends.append(claim)

        report["trends"] = cleaned_trends
        return report

    def _clean_evidence(self, evidence: Any, records: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        cleaned = []
        if isinstance(evidence, list):
            for item in evidence[:5]:
                if not isinstance(item, dict):
                    continue
                excerpt = str(item.get("excerpt", ""))[:600]
                source = str(item.get("source", "unknown"))
                source_url = str(item.get("source_url", ""))
                if excerpt:
                    cleaned.append({"source": source, "source_url": source_url, "excerpt": excerpt})
        if cleaned:
            return cleaned
        for record in records[:3]:
            excerpt = (record.get("clean_text") or record.get("raw_text") or "")[:300]
            if excerpt:
                cleaned.append({"source": str(record.get("source", "unknown")), "source_url": str(record.get("source_url", "")), "excerpt": excerpt})
        return cleaned

    def _normalize_level(self, value: Any) -> str:
        v = str(value or "low").lower()
        return v if v in {"high", "medium", "low"} else "low"

    def _normalize_score(self, value: Any) -> int:
        try:
            return max(0, min(100, int(value)))
        except Exception:
            return 0

    def _empty_report(self, reason: str) -> Dict[str, Any]:
        return {"agent": self.name, "type": "monitoring_report", "mode": "empty_input", "trends": [], "note": reason}

    def _deterministic_fallback(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        freq: Dict[str, int] = {}
        for r in records:
            for k in r.get("keywords", []):
                if len(str(k)) >= 4:
                    freq[str(k).lower()] = freq.get(str(k).lower(), 0) + 1

        sorted_terms = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
        trends = []
        for term, count in sorted_terms:
            evidence = [
                {"source": r.get("source", "unknown"), "source_url": r.get("source_url", ""), "excerpt": (r.get("clean_text") or r.get("raw_text", ""))[:200]}
                for r in records
                if term in [str(k).lower() for k in r.get("keywords", [])]
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

        return {"agent": self.name, "type": "monitoring_report", "mode": "deterministic_fallback_no_hf_token", "trends": trends}

    def _strength_from_count(self, count: int) -> str:
        if count >= 10:
            return "high"
        if count >= 5:
            return "medium"
        return "low"

    def _implication(self, term: str) -> str:
        return f"Increased discussion around '{term}' indicates a possible demand or friction signal for small businesses."

    def _recommendation(self, term: str) -> str:
        return f"Use '{term}' as a test theme in outreach messaging, then validate response with indicator codes before treating it as a proven market direction."
