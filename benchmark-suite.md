---
date: 2026-07-27
type: benchmark-suite
priority: ops-cs
---

# Benchmark Suite

Use these benchmarks to compare models for real recurring work. Prefer **real low-risk tasks** over synthetic prompts where possible.

## Scoring dimensions
Score each run 1-5 on:
- correctness
- grounding / evidence use
- stop-discipline
- format compliance
- latency
- operator cleanup burden
- recorded cost

Also record:
- whether escalation was required
- whether the output could have shipped internally without rewrite

## Benchmarks

### B1 — Internal scheduled-status draft
Goal:
- produce a concise internal first-pass status brief from known logs/artifacts

Why it matters:
- close to real ops work
- sensitive to latency, stop-discipline, and concise summarization

Pass criteria:
- brief is structurally usable
- no invented failures
- no meandering

### B2 — Morning brief component extraction
Goal:
- extract customer/account movement and produce bullet-ready input

Why it matters:
- high-frequency CS/ops workflow
- good target for cheaper first-pass models

Pass criteria:
- factual extraction is clean
- bullets are concise
- minimal cleanup before Hermes final synthesis

### B3 — Account-note update first draft
Goal:
- draft a suggested account-note update from bounded artifacts

Why it matters:
- core CS usage
- reveals whether a model can preserve customer-account note discipline

Pass criteria:
- direct-correlation discipline preserved
- no internal-only inference leaked into customer notes
- output remains bounded and structured

### B4 — Slack triage classification
Goal:
- classify inbound Slack/DM ask into route: answer directly, delegate, or schedule follow-up

Why it matters:
- latency-sensitive
- strong candidate for lower-cost models

Pass criteria:
- route is sensible
- privacy/excluded-channel rules preserved
- no over-answering

### B5 — Artifact / distribution audit synthesis
Goal:
- summarize evidence from S3/ECR/audit outputs into a practical operator summary

Why it matters:
- realistic ops task with structured evidence
- good test of bounded analysis and accuracy

Pass criteria:
- summary is evidence-based
- missing items are clearly called out
- no incorrect state claims

### B6 — OpenCode implementation prompt quality
Goal:
- produce or route a bounded implementation task with the right model/agent choice

Why it matters:
- tests coordination between Hermes routing and OpenCode execution

Pass criteria:
- chosen agent/model is sensible
- prompt is self-contained
- fallback decision is justified

### B7 — Planning / decomposition
Goal:
- turn an ambiguous ops task into a concrete plan with risks and validation steps

Why it matters:
- recurring front-door need
- reveals whether a model is fast but sloppy versus actually useful

Pass criteria:
- plan has dependencies, risks, validation
- stops cleanly
- does not pad with generic filler

## Benchmark cadence
- at least 2-3 runs per task family before promoting a model
- use both low-risk real tasks and small repeatable probes
- do not promote a model into scheduled-primary use from one clean run

## Promotion rule
Promote only if:
- quality is acceptable on repeated runs
- latency is materially better or cost is materially lower
- cleanup burden is consistently lower than the premium-model savings justify
