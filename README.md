---
date: 2026-09-22
type: project-note
status: active
---

# Model Ops

Purpose: continuously improve Hermes + OpenCode model selection for **ops** and **CS** workflows by reducing cost where safe, preserving reliability where required, and recording evidence instead of relying on intuition.

## Active Routing Configuration (September 2026)

### Provider Architecture
- **Unified Provider:** OpenRouter (BYOK) configured as sole provider across Hermes (`ops` & `ops-light`) and OpenCode (with SkillClaw proxy layer active on `:30000`).
- **Direct credentials removed:** All direct API keys (`openai-api`, `anthropic`, `deepinfra`, `gemini`) removed from `.env` files.

### Hermes Default Config (`ops` & `ops-light`)
- **Primary Intake Model:** `openrouter/google/gemini-3.8-flash`
- **Aliases:** `gemini-fast` (`gemini-3.8-flash`), `gemini-pro` (`gemini-2.5-pro`), `gemini-lite` (`gemini-2.5-flash-lite`), `gpt-5.4`, `gpt-5.6-luna`, `nemotron-super`, `luna`, `gemini-3.8-flash`, `glm-5.3-flash`, `ling-flash`, `ling-3-flash`, `mistral-nemo`
- **Fallback Chain:** `openrouter/z-ai/glm-5.3-flash` → `google/gemini-3.8-flash` → `openai/gpt-5.6-luna` → `openai/gpt-5.6-sol`
- **Mixture-of-Agents (MoA) Presets:**
  - `fast-ops` (Default): References `inclusionai/ling-3.0-flash` & `z-ai/glm-5.3-flash` → Aggregator `google/gemini-3.8-flash`
  - `frontier-review`: References `google/gemini-3.8-flash` & `z-ai/glm-5.3-flash` → Aggregator `openai/gpt-5.6-sol`
  - `claude-synthesis`: References `openai/gpt-5.6-sol` & `google/gemini-3.8-flash` → Aggregator `anthropic/claude-sonnet-4-6`
- **Max Output Tokens:** `16384`

### OpenCode Agent Alignment (`opencode.json`, verified 2026-09-22)
- **Base / Proxy:** `skillclaw/skillclaw-model` via `http://127.0.0.1:30000/v1`
- **Default Agent:** `build`
- **`build`:** `openrouter/openai/gpt-5.6-luna` (bounded implementation default; escalate high-stakes work to GPT-5.6 Sol/GPT-5.4)
- **`plan`:** `openrouter/google/gemini-2.5-pro` (analytical reasoning and architecture planning)
- **`cs-ops`:** `openrouter/google/gemini-3.6-flash` (rapid customer operations and ticket triage)
- **`solutions-architect`:** `openrouter/google/gemini-2.5-pro` (system boundary and architecture design)
- **`crogl-assistant`:** `openrouter/anthropic/claude-sonnet-4-6` (high-judgment cross-domain synthesis)
- **MCP Compatibility:** MCP server keys sanitized (`onepassword`, `google_calendar`, `aws_pricing`, `agentmemory`, `hubspot`, `jira`, `slack`, `gmail`, `granola`, `linkedin`) to fix protobuf schema validation across models.

### Automation & Background Jobs
- **Hermes Cron Jobs:**
  - `ops-morning-briefing`: `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free`
  - `ops-scheduled-status`: `openrouter/nvidia/nemotron-3-super-120b-a12b:free`
  - `openrouter-model-auditor`: `openrouter/nvidia/nemotron-3-super-120b-a12b:free`
  - `ops-account-auditor`: `openrouter/xiaomi/mimo-v2.5`
  - `sync-acmedemo-from-main`: `openrouter/openai/gpt-5.6-luna`
- **Launchd Background Sweeps:** 7 scripts in `vault/scripts/` updated to route through OpenRouter (`openrouter/qwen/qwen3.7-flash`, `openrouter/google/gemini-3.8-flash`, `openrouter/openai/gpt-5.6-luna`, `openrouter/openai/gpt-5.6-sol`).

## Main files
- `routing-matrix.md` — current task-family routing policy and MoA topology
- `eval-protocol.md` — standardized evaluation protocol, criteria, and test dataset for OpenRouter models
- `candidate-models-research.md` — research report on candidate models for future evaluations
- `benchmark-suite.md` — repeatable benchmarks (B1–B9)
- `experiment-log.md` — compact run-by-run evidence log
- `provider-expansion.md` — provider architecture and OpenRouter setup
- `scripts/check_openrouter_promos.py` — automated catalog ingestion, pricing calculator, and promo delta detector
- `scripts/eval_promo_candidates.py` — automated evaluation runner against B1–B9 benchmark probes with multi-round scoring, MoA compound evaluation, and eligibility gating
- `openrouter-model-inspector-plugin` (`/Users/jason/openrouter-model-inspector-plugin`) — native Hermes Desktop plugin for live promotional pricing, benchmark readiness (B1–B9), and multi-profile token usage telemetry
- `openrouter-model-auditor` — weekly cron job (`0 6 * * 1`) for continuous OpenRouter model catalog auditing and telemetry synchronization

## Roadmap & Forward Execution Plan

### Phase 1–5: Infrastructure, Policy & Core Benchmarks — **COMPLETED ✅**
- OpenRouter BYOK unified provider setup across Hermes & OpenCode.
- OpenCode MCP tool name sanitization (`onepassword`, `google_calendar`, `aws_pricing`).
- Mandatory repo-scoped delegation policy enforced.
- Core benchmarks B1–B7 executed and logged in `experiment-log.md`.
- Hermes cron jobs and 7 launchd background scripts updated to OpenRouter models.

### Phase 6: Telemetry & Cost Audit — **COMPLETED ✅**
- **Token Volume Audit:** SQLite queries verified token share shifted from legacy 99% GPT-5.4 usage to Gemini Flash / Luna / Free-tier routes.
- **Cost Reduction:** Validated >80% cost reduction against baseline spend.
- **Escalation Review:** Confirmed fallback escalation paths operate cleanly without silent degradation.

### Phase 7: Continuous Model Discovery, MoA & Alignment (Active)
- **New Model Probing:** Evaluate new open-weight and discounted releases on OpenRouter (e.g. GLM 5.3 Flash, Ling 3.0 Flash, Gemma 4) against benchmark suite probes (B1–B9).
- **Mixture-of-Agents Integration:** Maintain and evaluate compound MoA presets (`fast-ops`, `frontier-review`, `claude-synthesis`) on B9 arbitration probe.
- **Crogl Product Cross-Pollination:** Feed empirical benchmark findings into customer model selection and deployment blueprints.

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
