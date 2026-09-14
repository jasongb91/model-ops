---
date: 2026-07-27
type: reference
---

# Routing Matrix

## Reliability classes

### R0 — must land cleanly
Examples:
- scheduled jobs
- operator-facing morning/status briefs
- customer-facing summaries
- executive artifacts
- complex architecture planning / decomposition (B7)
- critical DevOps distribution / artifact integrity audits (B5)
- one-shot deliverables with low tolerance for cleanup

Default Primary Models (by task family):
- Scheduled Morning Brief / Status Synthesis: `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free`
- Planning / Architecture Decomposition (B7): `openrouter/google/gemini-3.7-flash` (Primary fast/low-cost) / `openrouter/openai/gpt-5.6-sol` (High-Judgment Frontier Specialist)
- Build / Orchestration Sweeps (`sync-acmedemo`): `openrouter/meituan/longcat-2.0`
- Account Reconciliation / Auditor: `openrouter/xiaomi/mimo-v2.5`
- Critical DevOps Integrity & Distribution Audits: `openrouter/openai/gpt-5.6-sol`

Fallbacks / Escalation Anchors:
- `openrouter/openai/gpt-5.6-sol` (Frontier quality upgrade for deep reasoning, architectural gotcha resolution, and empty checksum detection)
- `openrouter/google/gemini-3.7-flash` (Fast, high-context fallback lane)
- `openrouter/anthropic/claude-sonnet-4-6`

### R1 — important internal work
Examples:
- internal ops synthesis
- CS account-note drafting
- artifact/distribution audit summaries
- repo/workflow planning with verification
- long-context vault synthesis

Default low-cost / zero-cost lane:
- `openrouter/nvidia/nemotron-3-super-120b-a12b:free` (zero-cost primary)
- `openrouter/z-ai/glm-5.3-flash` ($0.075/$0.250 per 1M tokens — ultra-low-cost 1.31M context lane)
- `openrouter/openai/gpt-5.6-luna` ($0.20/$1.20 per 1M tokens — low-cost OpenAI primary)
- `openrouter/google/gemini-3.7-flash`
- `openrouter/xiaomi/mimo-v2.5`
- `deepinfra/openai/gpt-oss-120b`
- `deepinfra/Qwen/Qwen3-Next-80B-A3B-Instruct`
- `deepinfra/Qwen/Qwen3-Coder-480B-A35B-Instruct-Turbo`

Escalate to:
- `openrouter/openai/gpt-5.6-sol`
- `openrouter/google/gemini-3.7-flash`
- `anthropic/claude-sonnet-4-6`

### R2 — low-risk exploratory / bounded internal work
Examples:
- classification
- extraction
- draft bullets
- smoke probes
- structured comparison tasks

Default:
- `openrouter/nvidia/nemotron-3-super-120b-a12b:free` (zero-cost primary)
- `openrouter/z-ai/glm-5.3-flash` ($0.075/$0.250 per 1M tokens — fast sub-second extraction & schema-compliant triage)
- `openrouter/openai/gpt-5.6-luna` ($0.20/$1.20 per 1M tokens — fast, 100% extraction accuracy)
- `openrouter/xiaomi/mimo-v2.5` / `openrouter/qwen/qwen3.7-flash` (low-cost sub-$0.25/1M)
- cheapest / fastest validated open-weight option for the task family

## Task-family policy

| Task family | Reliability class | First model | Alternate open-weight / low-cost | Premium fallback | Notes |
|---|---:|---|---|---|---|
| Scheduled status / morning brief final output | R0 | `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` | `openrouter/z-ai/glm-5.3-flash` (shadow-gated) / `openrouter/google/gemini-3.7-flash` | `openrouter/openai/gpt-5.6-sol` | Nemotron 3 Ultra 550B ($0 cost) is primary for morning brief; GLM 5.3 Flash ($0.075/1M, 5.0/5 on B1) admitted for 3-day shadow evaluation; Gemini 3.7 Flash ($0.075/1M) is alternate fast synthesis. GPT-5.6 Sol retained as premium fallback. |
| Granola transcript to meeting note processing | R1 | `openrouter/minimax/minimax-m3` | `openrouter/openai/gpt-5.6-luna` / `openrouter/google/gemini-3.7-flash` | `openrouter/openai/gpt-5.6-sol` | MiniMax M3 achieved 4.95/5 with 100% attendee attribution at 16.8s. GPT-5.6 Luna ($0.20/$1.20) and Gemini 3.7 Flash provide secondary long-context support. |
| Scheduled account decay & archive sweep | R1 | `openrouter/poolside/laguna-s-2.1` | `openrouter/xiaomi/mimo-v2.5` / `deepinfra/deepseek-ai/DeepSeek-V3.2` | `openrouter/google/gemini-3.7-flash` | Laguna S 2.1 demonstrated 4.96/5 with 100% bullet immutability and precise 180-day contact aging at 14.1s ($0.090/$0.200/1M). |
| Scheduled end-of-day (EOD) progress sweep | R1 | `openrouter/poolside/laguna-s-2.1` | `openrouter/xiaomi/mimo-v2.5` / `openrouter/qwen/qwen3.7-flash` | `openrouter/google/gemini-3.7-flash` | Laguna S 2.1 scored 4.97/5 with 100% bullet immutability, in-place canonical updates, and clean canvas sync integration. |
| Customer account auditor & reconciliation | R0/R1 | `openrouter/xiaomi/mimo-v2.5` | `openrouter/google/gemini-3.7-flash` | `openrouter/openai/gpt-5.6-sol` | MiMo-V2.5 validated for fast note triage and canonical vault mutations. Gemini 3.7 Flash as low-cost secondary. |
| Internal ops status synthesis (B1) | R1 | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` | `openrouter/z-ai/glm-5.3-flash` / `openrouter/openai/gpt-5.6-luna` / `openrouter/google/gemini-3.7-flash` | `openrouter/openai/gpt-5.6-sol` | Nemotron 3 Super 120B provides zero API cost; GLM 5.3 Flash (5.0/5, 0.22s) and GPT-5.6 Luna ($0.20/$1.20) provide high-accuracy low-cost lanes. GPT-5.6 Sol is frontier escalation. |
| CS note drafting / account update first pass (B3) | R1 | `openrouter/google/gemini-3.7-flash` | `openrouter/z-ai/glm-5.3-flash` / `openrouter/openai/gpt-5.6-luna` / `openrouter/xiaomi/mimo-v2.5` | `openrouter/openai/gpt-5.6-sol` | Gemini 3.7 Flash, GLM 5.3 Flash, and GPT-5.6 Luna (100% canonical structure, 0.61s latency) match frontier quality at ~90% cost savings. |
| DevOps / distribution audits (B5) | R1/R0 | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` (R1) / `openrouter/openai/gpt-5.6-sol` (R0) | `openrouter/z-ai/glm-5.3-flash` / `openrouter/google/gemini-3.7-flash` / `openrouter/xiaomi/mimo-v2.5` | `openrouter/openai/gpt-5.6-sol` | Nemotron 3 Super is zero-cost R1 default. GLM 5.3 Flash (5.0/5 on B5) provides ultra-fast audit synthesis. GPT-5.6 Sol is R0 frontier specialist for detecting empty sha256 checksums and deep integrity audits. |
| Slack triage / categorization / extraction (B2/B4) | R2 | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` or `openrouter/z-ai/glm-5.3-flash` | `openrouter/openai/gpt-5.6-luna` / `openrouter/xiaomi/mimo-v2.5` / `openrouter/qwen/qwen3.7-flash` | `openrouter/google/gemini-3.7-flash` | Nemotron 3 Super (3.6s, $0), GLM 5.3 Flash (0.34s, 5.0/5 JSON, $0.075/1M), and GPT-5.6 Luna (0.49s, $0.20/$1.20) deliver rapid extraction and schema-compliant triage. |
| Muse Glimmer triage / extraction / bounded ops chat (B2/B4) | R2 | `openrouter/meta/muse-glimmer-30b:deepinfra/bf16` | `openrouter/nvidia/nemotron-3-super-120b-a12b:free` / `openrouter/qwen/qwen3.7-flash` | `openrouter/google/gemini-3.7-flash` | Muse Glimmer scored 5.0/5 on B2 and B4 with 100% assertion passes and 0.21–0.29s latency in a single-run evaluation; provider pricing is listed as $0.30/$1.20 per 1M, while this evaluation recorded $0.00. Keep bounded until repeated-run stability is established. |
| Build / implementation-heavy OpenCode run | R0/R1 | `openrouter/openai/gpt-5.6-luna` (bounded default) | `openrouter/poolside/laguna-s-2.1` / `openrouter/meituan/longcat-2.0` | `openrouter/openai/gpt-5.6-sol` | GPT-5.6 Luna is the verified lower-cost OpenCode build default ($0.20/$1.20 per 1M tokens). Use only for bounded, test-backed changes; escalate to Sol for high-stakes architecture, security, customer-facing, or repeated verification failure. |
| Planning / architecture decomposition (B7) | R0 | `openrouter/google/gemini-3.7-flash` | `openrouter/openai/gpt-5.6-sol` / `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` | `openrouter/openai/gpt-5.6-sol` / `anthropic/claude-sonnet-4-6` | Gemini 3.7 Flash is fast standard. GPT-5.6 Sol is frontier reasoning specialist resolving Fargate/EC2 IMDS boundaries and complex IAM constraints. |
| Architecture / infra tradeoff work | R0 | `openrouter/openai/gpt-5.6-sol` or `anthropic/claude-sonnet-4-6` | `openrouter/google/gemini-3.7-flash` | `openai/o3` class if added later | GPT-5.6 Sol and Claude Sonnet 4.6 serve as frontier anchors for high-ambiguity architectural trade-offs. |
| Long-context vault / multi-document synthesis (B6) | R1 | `openrouter/google/gemini-3.7-flash` | `openrouter/openai/gpt-5.6-luna` / `openrouter/minimax/minimax-m3` | `openrouter/openai/gpt-5.6-sol` | Gemini 3.7 Flash (1M+ window) and GPT-5.6 Luna (100% needle recall @ 1.05M window, $0.20/$1.20) provide fast, low-cost long-context synthesis. |
| Crogl/debug/provider-compatibility analysis | R1 | `openrouter/google/gemini-3.7-flash` | `openrouter/meituan/longcat-2.0` / `deepinfra/openai/gpt-oss-120b` | `openrouter/openai/gpt-5.6-sol` | Fast diagnostic triage with low token cost. |

## Promotion Criteria & Staged Rollout Policy

To continuously capture promotional discounts, free routes, and generational price reductions on OpenRouter without compromising operational reliability or data safety, all candidate models follow a strict staged rollout policy governed by their benchmark evaluation scores (B1–B8) and task reliability class (R0, R1, R2).

```
 ┌──────────────────────────────────────────────────────────────┐
 │ OpenRouter Catalog & Promo Ingestion (check_openrouter_promos)│
 └──────────────────────────────┬───────────────────────────────┘
                                │ Candidate Discovery (>=20% drop, free route, low-cost)
                                ▼
 ┌──────────────────────────────────────────────────────────────┐
 │ Automated Benchmark Evaluation (eval_promo_candidates.py)    │
 │ Multi-round scoring across B1–B8 on 7 standard dimensions    │
 └──────────────────────────────┬───────────────────────────────┘
                                │
        ┌───────────────────────┴───────────────────────┐
        │ Score >= 4.8                                  │ Score >= 4.8
        ▼                                               ▼
 ┌──────────────────────────────┐                ┌──────────────────────────────┐
 │ Fast-Track R2 Lane           │                │ Fast-Track R1 Lane           │
 │ - Chat defaults & aliases    │                │ - Internal ops synthesis     │
 │ - Frontdoor triage (B4)      │                │ - Vault note drafts (B3)     │
 │ - Component extraction (B2)  │                │ - Long-context review (B6)   │
 └──────────────────────────────┘                └──────────────┬───────────────┘
                                                                │
                                                                │ Score >= 4.9 & 0-cleanup
                                                                ▼
                                                 ┌──────────────────────────────┐
                                                 │ Shadow-Gate R0 Lane          │
                                                 │ - Scheduled mutating crons   │
                                                 │ - Morning briefs & executive │
                                                 │ - 3-day shadow evaluation    │
                                                 │ - Retain GPT-5.4/Sonnet      │
                                                 │   fallback anchors           │
                                                 └──────────────────────────────┘
```

### 1. Fast-Track Promotion Path (R2 & R1 Lanes)
Candidate models achieving a benchmark rubric score of **$\ge 4.8$ / 5.0** across their target probe suites are fast-tracked into interactive, bounded, and draft operational workflows:

- **R2 Fast-Track (Triage, Classification & Extraction):**
  - **Eligibility Gate:** Benchmark score $\ge 4.8$ on Probes B2 (Extraction) and B4 (Triage / JSON Schema) with 100% format compliance (0 JSON parse failures, 0 schema deviations).
  - **Applied Scope:** Inbound frontdoor triage, Slack message classification, chat alias defaults (`/ops-frontdoor`, `gemini-lite`, `fast-triage`), and bounded entity extraction.
  - **Rollout Action:** Promoted immediately as primary or co-default in `routing-matrix.md` for R2 task families upon test suite verification.

- **R1 Fast-Track (Internal Synthesis, Drafting & Tool Execution):**
  - **Eligibility Gate:** Benchmark score $\ge 4.8$ across relevant R1 probes (B1 Status Synthesis, B3 Vault Account Notes, B5 Audit Synthesis, B6 Long-Context Recall, B7 Decomposition, B8 Tool Calling) with $\ge 4.5$ stop-discipline and zero critical hallucinations on entities, IPs, or file paths.
  - **Applied Scope:** Interactive CS account-note drafting, internal ops status compilation, distribution matrix audits, OpenCode worker execution, and long-context multi-document reviews.
  - **Rollout Action:** Promoted as default low-cost primary or secondary specialist in `routing-matrix.md`.

### 2. Shadow-Gating Policy (R0 Production Sweeps & Mutating Crons)
R0 tasks represent high-judgment, mutating, or executive-facing workflows where errors cause customer-visible drift, silent data corruption, or broken infrastructure state (e.g. `ops-morning-briefing`, scheduled launchd mutations, executive briefs, automated vault reconciliations).

- **Promotion Gate ($\ge 4.9$ + Zero Cleanup):**
  - Benchmark score $\ge 4.9$ / 5.0 across all core operational probes (B1, B3, B5, B7, B8).
  - Operator Cleanup Burden score of 5.0 (100% shippable without manual edits).
  - Validated rate-limit resiliency under burst concurrency on OpenRouter.

- **Mandatory 3-Day Shadow Execution Window:**
  - Before a promo candidate replaces an R0 primary, it must run in shadow mode for at least **3 consecutive execution cycles** alongside the active primary.
  - Shadow outputs are automatically diffed against the baseline run for grounding precision, date accuracy, bullet immutability, and formatting regressions.
  - Free-tier endpoints (`:free`) subject to HTTP 429 concurrency throttling are restricted to shadow/draft modes and barred from autonomous mutating cron jobs.

- **Permanent Frontier Fallback Anchors:**
  - All R0 and scheduled mutating workflows MUST retain explicit, hardcoded fallback ladders to frontier models:
    - Primary Escalation Anchor: `openrouter/openai/gpt-5.6-sol` (R0 Frontier) or `openrouter/google/gemini-3.7-flash` (R1 High-Context)
    - Secondary Escalation Anchor: `openrouter/anthropic/claude-sonnet-4-6`
  - Automatic fallback triggers on:
    1. HTTP 400, 429, 500, 502, or 503 provider errors from OpenRouter.
    2. Two consecutive schema or assertion verification failures.
    3. Latency exceeding 2x the task-family latency budget.

---

## Escalation triggers
Escalate immediately when any of these appear:
- obvious file/tool grounding gaps
- weak stop-discipline
- poor formatting control
- output needs customer/executive tone
- verification burden exceeds the savings
- repeated provider slowness or transient failures

## Current route concerns
- `deepinfra/deepseek-ai/DeepSeek-V3.2` is too slow for many interactive ops/CS cases
- `opencode/big-pickle` is currently flaky and should remain evaluation-only
- current Hermes fallback chain is reliability-oriented, not cost-optimized

## Muse Glimmer 30B qualification (2026-08-27)

`meta/muse-glimmer-30b` via the verified OpenRouter DeepInfra `deepinfra/bf16` endpoint is qualified for the R2 triage/extraction fast-track only. It achieved an overall 4.52/5.0 across B2, B3, B4, B5, and B8, with 84% aggregate assertion pass rate and 0.29s average latency in the captured single-run evaluation. B2 (5.0/5), B4 (5.0/5), B5 (5.0/5), and B8 (5.0/5) were clean; B3 scored 2.58/5 with empty output and passed only the no-speculation assertion.

Routing boundary:
- Use for bounded extraction, frontdoor/Slack classification, internal ops digest components, distribution-audit synthesis, and structured tool-call drafting where a verifier remains in the loop.
- Do not use for canonical CS account-note drafting, vault mutations, unattended R1/R0 scheduled jobs, or customer-facing finalization until B3 passes on repeated canonical-fixture runs.
- Retain the normal R2 fallback ladder and escalate on empty output, schema/assertion failure, provider errors, or latency beyond the task-family budget. The endpoint's verified provider rate card is $0.30/M input and $1.20/M output; the benchmark's $0.00 is recorded evaluation cost, not a production pricing guarantee.

## Z.ai GLM 5.3 Flash qualification (2026-09-11)

`z-ai/glm-5.3-flash` evaluated via OpenRouter (DeepInfra upstream) scored 4.89/5.0 overall with 0.41s average latency and 96.0% assertion pass rate across B1, B2, B4, B5, and B8 (15 total runs across 3 rounds).
- Rate card: $0.075 / 1M input, $0.250 / 1M output, 1.31M context window.
- B1 (Status Digest, R1): 5.00/5.0 (100% assertions, 0.22s). Clean infrastructure and cron status extraction.
- B2 (Morning Brief Extraction, R2): 4.45/5.0 (80% assertions, 0.73s). Minor date abbreviation variance ("Sept" vs "September").
- B4 (Frontdoor / Slack Triage, R2): 5.00/5.0 (100% assertions, 0.34s). Perfect JSON schema adherence and priority classification.
- B5 (DevOps Distribution Audit, R1): 5.00/5.0 (100% assertions, 0.29s). Clean table structure, exact anomaly detection.
- B8 (Agent Tool Use, R1): 5.00/5.0 (100% assertions, 0.45s). Accurate tool schema parameter population.

Routing boundary:
- Promoted into R2 fast-track extraction/triage co-default.
- Promoted into R1 internal ops synthesis and audit drafting lanes.
- Admitted to R0 shadow evaluation for scheduled morning briefs alongside `nemotron-3-ultra-550b:free` and `gemini-3.7-flash`, retaining hardcoded frontier fallbacks (`gpt-5.4` / `gpt-5.6-sol` / `claude-sonnet-4-6`).

## InclusionAI Ling 3.0 Flash qualification (2026-09-14)

`inclusionai/ling-3.0-flash` evaluated via OpenRouter scored 4.91/5.0 overall with 0.31s average latency and 97% assertion pass rate across the B1-B8 benchmark suite.

Routing boundary:
- Qualified for the R1 fast-track as a low-cost internal synthesis and drafting candidate.
- Admitted to R0 shadow evaluation only; do not use as the autonomous primary for mutating or operator-facing scheduled workflows until it completes the required three consecutive shadow cycles with zero material cleanup.
- Retain explicit frontier fallbacks (`gpt-5.4` / `gpt-5.6-sol` / `claude-sonnet-4-6`) throughout shadow evaluation.
- Treat the 2026-09-14 benchmark as live provider evidence. The contemporaneous `thinkingmachines/inkling-small:free` and `thinkingmachines/inkling:free` probes were rejected because OpenRouter returned HTTP 403 outside an approved agentic harness.

## Planned expansion candidates
See `provider-expansion.md` before changing defaults.
