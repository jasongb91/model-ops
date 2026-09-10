---
date: 2026-07-27
type: project-note
status: active
---

# Model Ops

Purpose: continuously improve Hermes + OpenCode model selection for **ops** and **CS** workflows by reducing cost where safe, preserving reliability where required, and recording evidence instead of relying on intuition.

## Active Routing Configuration (July 28, 2026)

### Provider Architecture
- **Unified Provider:** OpenRouter (BYOK) configured as sole provider across Hermes (`ops` & `ops-light`) and OpenCode.
- **Direct credentials removed:** All direct API keys (`openai-api`, `anthropic`, `deepinfra`, `gemini`) removed from `.env` files.

### Hermes Default Config (`ops` & `ops-light`)
- **Primary Intake Model:** `openrouter/google/gemini-3.7-flash`
- **Aliases:** `gemini-fast`, `gemini-pro`, `gemini-lite`, `gpt-5.4`, `sonnet`, `luna`
- **Max Output Tokens:** `16384`

### OpenCode Agent Alignment (`opencode.json`, verified 2026-09-01)
- **`cs-ops`:** `openrouter/google/gemini-3.7-flash`
- **`plan`:** `openrouter/google/gemini-3.7-flash`
- **`solutions-architect`:** `openrouter/google/gemini-3.7-flash`
- **`build`:** `openrouter/openai/gpt-5.6-luna` (bounded implementation default; escalate high-stakes work to GPT-5.6 Sol/GPT-5.4)
- **`crogl-assistant`:** `openrouter/anthropic/claude-sonnet-4-6`
- **MCP Compatibility:** MCP server keys sanitized (`onepassword`, `google_calendar`, `aws_pricing`) to fix Google Gemini protobuf function-name validation.

### Automation & Background Jobs
- **Hermes Cron Jobs:** `ops-morning-briefing` (`openrouter/nvidia/nemotron-3-ultra-550b-a55b:free`), `ops-scheduled-status` (`openrouter/nvidia/nemotron-3-super-120b-a12b:free`).
- **Launchd Background Sweeps:** 7 scripts in `vault/scripts/` updated to route through OpenRouter (`openrouter/qwen/qwen3.7-flash`, `openrouter/google/gemini-3.7-flash`, `openrouter/openai/gpt-5.6-luna`, `openrouter/openai/gpt-5.6-sol`).

## Main files
- `routing-matrix.md` — current task-family routing policy
- `eval-protocol.md` — standardized evaluation protocol, criteria, and test dataset for OpenRouter models
- `candidate-models-research.md` — research report on candidate models for future evaluations
- `benchmark-suite.md` — repeatable benchmarks (B1–B8)
- `experiment-log.md` — compact run-by-run evidence log
- `provider-expansion.md` — provider architecture and OpenRouter setup
- `scripts/check_openrouter_promos.py` — automated catalog ingestion, pricing calculator, and promo delta detector
- `scripts/eval_promo_candidates.py` — automated evaluation runner against B1–B8 benchmark probes with 7-dimension scoring and eligibility gating
- `openrouter-model-inspector-plugin` (`/Users/jason/openrouter-model-inspector-plugin`) — native Hermes Desktop plugin for live promotional pricing, benchmark readiness (B1–B8), and multi-profile token usage telemetry
- `openrouter-model-auditor` — weekly cron job (`0 6 * * 1`) for continuous OpenRouter model catalog auditing and telemetry synchronization

## Roadmap & Forward Execution Plan

### Phase 1–5: Infrastructure, Policy & Core Benchmarks — **COMPLETED ✅**
- OpenRouter BYOK unified provider setup across Hermes & OpenCode.
- OpenCode MCP tool name sanitization (`onepassword`, `google_calendar`, `aws_pricing`).
- Mandatory repo-scoped delegation policy enforced.
- Core benchmarks B1–B7 executed and logged in `experiment-log.md`.
- Hermes cron jobs and 7 launchd background scripts updated to OpenRouter models.

### Phase 6: 7-Day Telemetry & Cost Audit (Scheduled: August 4, 2026)
- **Token Volume Audit:** Execute SQLite queries on Hermes `state.db` and OpenCode DB to measure actual token share shift away from legacy 99% GPT-5.4 usage.
- **Cost Reduction Calculation:** Compare post-migration 7-day spend against the $548/14-day baseline recorded on July 27.
- **Escalation Review:** Audit `experiment-log.md` for any background OpenCode dispatches that triggered fallback escalation.

### Phase 7: Continuous Model Discovery & Crogl Product Alignment (Ongoing)
- **New Model Probing:** Evaluate new open-weight model releases on OpenRouter (e.g. future Qwen, DeepSeek, or Llama iterations) against B2 (extraction) and B4 (triage) benchmarks before updating `routing-matrix.md`.
- **Crogl Product Cross-Pollination:** Feed empirical benchmark findings (such as Gemini 3.6 Flash's 18s processing time and 100% needle recall on 30k tokens) into Crogl product architecture notes for customer model selection.

## Related Sessions
- Session ID: `@session:ops/20260727_094031_024d18`
  - Title: **Model routing for cost optimization / Model Ops execution**
  - Project Workspace: `Model Ops` (`/Users/jason/model-ops`)
  - Description: Established the unified OpenRouter BYOK architecture, executed benchmarks B1 through B7, configured OpenCode agents, sanitized MCP tool schemas, and updated Hermes cron/launchd background jobs.

## Operating rule
1. start with the routing matrix
2. run benchmarks on real low-risk work where possible
3. escalate when output quality, control, or reliability is insufficient
4. record the outcome in `experiment-log.md`
5. update the routing matrix only after repeat evidence
