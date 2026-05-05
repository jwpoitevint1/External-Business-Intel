# CV 1.1 Human-Centered AI Governance Note

## Core Position

AI is not treated as inherently dangerous in this system. The risk comes from unbounded AI use inside uncontrolled workflows, especially when probabilistic output is treated as deterministic truth.

CV 1.1 exists to protect the people using AI by forcing the system to produce bounded, traceable, decision-support-grade outputs.

## Operating Principle

The model is not the decision-maker. The model is an input to a human decision process.

The system therefore enforces:

- defined scope
- controlled constraints
- evidence-bound output
- structured schemas
- fail-closed or deterministic fallback behavior
- human-in-the-loop review before operational action

## Scope vs Constraint

Scope defines what an AI component is allowed to do.

Constraint defines how that AI component is allowed to do it.

Applied to the current system:

- DeepSeek remains a local ETL wrapper only.
- DeepSeek performs extraction, normalization, deduplication, and validation.
- DeepSeek does not interpret, recommend, or decide.
- Qwen is scoped as a tactical analyst only.
- Qwen analyzes normalized, source-bound, public-domain evidence.
- Qwen does not mutate, rewrite, normalize, extract, load, or delete records.
- Qwen must return structured outputs with evidence, confidence, score, implication, and recommended action.

## Human Protection Logic

The guardrails are not designed for the AI as an abstract entity. They are designed for the human operator using the AI.

The system protects the operator from:

- overtrusting model output
- acting on unsupported claims
- confusing opinion signals with verified facts
- accepting hallucinated sources
- using private or non-public data unintentionally
- allowing model drift to enter downstream decisions

## Current External Business Intel Application

The External Business Intel system follows this chain:

```text
public-domain data -> policy validation -> deterministic ETL -> constrained Qwen analysis -> Neon storage -> UI review -> human action
```

This keeps AI as an analytical component, not an autonomous authority.

## CV 1.1 Alignment

This implementation aligns with CV 1.1 by enforcing:

- public-source validation
- prohibited data blocking
- role-scoped model behavior
- evidence binding
- fallback behavior when model execution fails
- human review before decision or action

The objective is not to make AI harmless by assumption. The objective is to make AI use controlled, auditable, and bounded enough for practical business decision support.
