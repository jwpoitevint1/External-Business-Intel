from dataclasses import dataclass
from typing import Any, Dict, Iterable


class CV11PolicyError(ValueError):
    pass


@dataclass(frozen=True)
class AgentScope:
    name: str
    allowed_actions: set[str]
    forbidden_actions: set[str]
    allowed_outputs: set[str]


DEEPSEEK_ETL_SCOPE = AgentScope(
    name="deepseek_etl",
    allowed_actions={"extract", "normalize", "deduplicate", "validate", "load"},
    forbidden_actions={
        "analyze",
        "recommend",
        "report",
        "opinion",
        "interpret_market",
        "invent",
        "overwrite_source",
        "delete_source",
        "mutate_raw_data",
        "fabricate_source",
    },
    allowed_outputs={"normalized_record", "validation_report", "load_result"},
)

QWEN_ANALYST_SCOPE = AgentScope(
    name="qwen_analyst",
    allowed_actions={"analyze", "classify", "summarize", "recommend", "monitor", "report"},
    forbidden_actions={
        "extract",
        "normalize",
        "deduplicate",
        "load",
        "mutate_raw_data",
        "overwrite_source",
        "delete_source",
        "fabricate_source",
    },
    allowed_outputs={"trend_analysis", "recommendation", "monitoring_report", "risk_note"},
)


def assert_action_allowed(scope: AgentScope, action: str) -> None:
    if action in scope.forbidden_actions or action not in scope.allowed_actions:
        raise CV11PolicyError(f"CV 1.1 scope violation: {scope.name} cannot perform action '{action}'.")


def assert_output_allowed(scope: AgentScope, output_type: str) -> None:
    if output_type not in scope.allowed_outputs:
        raise CV11PolicyError(f"CV 1.1 output violation: {scope.name} cannot emit '{output_type}'.")


def require_source_binding(records: Iterable[Dict[str, Any]]) -> None:
    for record in records:
        if not record.get("source") or not record.get("source_url"):
            raise CV11PolicyError("CV 1.1 source-binding violation: every record requires source and source_url.")
        if not record.get("observed_at"):
            raise CV11PolicyError("CV 1.1 temporal-binding violation: every record requires observed_at.")


def refuse_if_unsourced_claim(claim: Dict[str, Any]) -> None:
    evidence = claim.get("evidence") or []
    if not evidence:
        raise CV11PolicyError("CV 1.1 refusal: analyst claim lacks evidence.")


def immutable_data_update_guard(existing: Dict[str, Any], incoming: Dict[str, Any]) -> None:
    protected_fields = {"raw_text", "source", "source_url", "observed_at"}
    for field in protected_fields:
        if field in existing and field in incoming and existing[field] != incoming[field]:
            raise CV11PolicyError(f"CV 1.1 immutability violation: cannot mutate protected field '{field}'.")
