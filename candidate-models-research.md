---
date: 2026-08-21
type: research-report
status: active
priority: ops-cs
---

# Candidate Models for Future Model Ops Evaluations

## Executive Summary

To sustain continuous cost optimization and routing enhancements for Hermes Agent and OpenCode across CS and Operations workflows, this research evaluates emerging and high-volume models available on OpenRouter and related inference platforms (as of August 2026).

Prior evaluations established `google/gemini-3.6-flash` and `qwen/qwen3.7-flash` as dominant low-cost / high-throughput workhorses for extraction (B2), account updates (B3), triage (B4), and long-context synthesis (B6), with `openai/gpt-5.4` and `anthropic/claude-sonnet-4-6` serving as frontier R0 anchors. Sibling evaluation tasks (`t_247d87ed` and `t_4594b2cc`) benchmarked `nvidia/nemotron-3` and `xiaomi/mimo-v2.5`.

This report identifies **top candidate models** not yet formally evaluated in Model Ops, structured across specific operational task profiles:
1. **Ultra-Low Cost / High-Speed Extraction & Triage (R2)**
2. **Long-Context Vault Synthesis & Telemetry Auditing (R1)**
3. **Agentic Coding, Tool Use & Complex Decomposition (R1/OpenCode)**
4. **Frontier Fallback & High-Stakes Planning (R0)**

---

## 1. Candidate Comparison Matrix

| Model Slug / Name                 | Provider / Lab  |  Context Window  |  Input Cost (/1M)   | Output Cost (/1M) | Primary Ops Niche                        | Key Differentiators & Strengths                                                                               | Risk / Considerations                                                      |
| --------------------------------- | --------------- | :--------------: | :-----------------: | :---------------: | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `deepseek/deepseek-v4-flash-0731` | DeepSeek        | 1,310,720 (1.3M) |       $0.065        |      $0.140       | R2 Triage, Fast Extraction, Bulk Logs    | 284B total / 13B active MoE; ultra-low pricing; 1.3M context; prompt caching ($0.0168/M).                     | Latency variability across OpenRouter host nodes; needs tool schema check. |
| `google/gemma-4-26b-a4b-it`       | Google DeepMind |  262,144 (256k)  | $0.070 (or `:free`) |      $0.340       | R2 Local/Shadow Triage & Extraction      | 25.2B total / 3.8B active MoE; 85+ t/s decode; exceptional lightweight efficiency; free tier available.       | 16k output token cap; smaller capacity for nuanced enterprise planning.    |
| `poolside/laguna-s-2.1`           | Poolside        |  1,048,576 (1M)  | $0.090 (or `:free`) |      $0.200       | OpenCode Coding & Tool Execution         | 118B total / 8B active MoE; built specifically for agentic coding; 70.2% Terminal-Bench 2.1; 1M context.      | Coding specialist; less tested on general natural language CS prose.       |
| `stepfun/step-3.7-flash`          | StepFun         |  262,144 (256k)  |       $0.200        |      $1.150       | R1 Multi-Modal Telemetry & Tool Chains   | 196B total / 11B active MoE; native multi-modal; robust multi-step function calling; low latency.             | Output pricing higher than DeepSeek/Gemma; 256k context ceiling.           |
| `minimax/minimax-m3`              | MiniMax         |  1,048,576 (1M)  |       $0.230        |      $0.960       | R1 Long-Context Ops Synthesis            | 1M context with 262k max output; strong multi-document reasoning; robust multi-provider backing.              | Cost-effective for 1M context, but slightly slower TTFT on dense inputs.   |
| `meituan/longcat-2.0`             | Meituan         |  128,000 (128k)  |       $0.300        |      $1.200       | OpenCode / R1 Agentic Coding & Workflows | 1.6T total / 48B active MoE; unmasked "Owl Alpha" stealth leader; outstanding tool calling & agent execution. | 128k context limit; higher memory footprint across providers.              |
| `meta/muse-glimmer-30b:deepinfra/bf16` | Meta / DeepInfra | 131,072 (128k) | $0.300 | $1.200 | R2 Triage, Extraction & Bounded Tool Drafting | Evaluated via OpenRouter with 5.0/5 on B2, B4, B5, and B8, 0.29s average latency, and 100% assertion passes on those probes. | B3 canonical account-note run produced empty output (2.58/5, 1/5 assertions); single-run evidence does not establish repeated-run stability or R1 suitability. |
| `kwaipilot/kat-coder-air-v2.5`    | Kwaipilot       |  262,144 (256k)  |       $0.150        |      $0.600       | OpenCode Light Coding & Script Sweeps | Fast coding MoE tuned for automated issue resolution and git workflows; competitive pricing.                  | Focused on code/diff generation; not suitable for CS tone/narrative.    |
| `moonshotai/kimi-k3`              | Moonshot AI     |  262,144 (256k)  |       $3.000        |      $15.000      | R0 Complex Ops Planning & Architecture   | Frontier-class reasoning engine; deep step-by-step verification; top-tier mathematical & logic precision.     | Premium cost tier; slower decode due to deep chain-of-thought exploration. |

---

## 2. Deep-Dive by Operational Task Family

### A. Ultra-Low-Cost Extraction, Triage & Slack Intake (R2 Lane)
- **Top Candidates:** `deepseek/deepseek-v4-flash-0731` & `google/gemma-4-26b-a4b-it`
- **Rationale:** Current R2 relies on `qwen/qwen3.7-flash` ($0.20–$0.30/M) and `gemini-3.6-flash`. DeepSeek V4 Flash cuts input costs to **$0.065/M** with a **1.3M context window**, allowing entire multi-day log dumps to be parsed for pennies. Gemma 4 26B provides an ultra-fast **3.8B active parameter** path with an OpenRouter free endpoint (`google/gemma-4-26b-a4b-it:free`) ideal for non-blocking shadow triage.
- **Recommended Benchmark Focus:** Probe B2 (Extraction) & Probe B4 (Slack Triage / JSON schema compliance).

### B. High-Volume Long-Context Vault & Ops Synthesis (R1 Lane)
- **Top Candidates:** `minimax/minimax-m3` & `stepfun/step-3.7-flash`
- **Rationale:** MiniMax M3 offers **1M token context** with up to **262k token generation** at $0.23/M input. For multi-document vault audits, customer account rollups, and distribution matrix audits (Probe B5/B6), M3 offers a viable alternative to Gemini Flash without vendor concentration. Step 3.7 Flash brings high-reliability function calling and multi-modal analysis (e.g. inspecting system architecture diagrams or telemetry charts).
- **Recommended Benchmark Focus:** Probe B1 (Ops Status Digest), Probe B5 (Distribution Audit), and Probe B6 (Needle Recall).

### C. Agentic Coding & OpenCode Worker Execution (R1/Worker Lane)
- **Top Candidates:** `poolside/laguna-s-2.1`, `meituan/longcat-2.0`, & `kwaipilot/kat-coder-air-v2.5`
- **Rationale:** OpenCode currently relies on `qwen3-coder` or premium `gpt-5.4`. Poolside's Laguna S 2.1 (118B-A8B) is purpose-built for CLI coding and SWE benchmarks, supporting 1M context at $0.09/M input. Meituan's LongCat 2.0 (1.6T-A48B) demonstrated top-ranked agent performance on OpenRouter under its "Owl Alpha" stealth testing, excelling at multi-turn terminal execution.
- **Recommended Benchmark Focus:** Probe B7 (Architecture Planning) & Probe B8 (Tool Use / Function Calling).

### D. Frontier Reasoning & Complex Architecture (R0 Fallback Lane)
- **Top Candidates:** `moonshotai/kimi-k3`
- **Rationale:** Serves as a direct benchmark challenger to `gpt-5.4` and `claude-sonnet-4-6` for high-stakes GovCloud migrations, complex refactoring plans, and executive briefs where zero-defect output overrides latency.
- **Recommended Benchmark Focus:** Probe B7 (Planning & Decomposition).

---

## 3. Recommended Phased Evaluation Pipeline

1. **Phase 1: Rapid R2 / Triage Smoke Sweep (Immediate)**
   - Benchmark `deepseek/deepseek-v4-flash-0731` and `google/gemma-4-26b-a4b-it` against Probe B2 and Probe B4.
   - *Target:* Verify strict JSON output schema conformance and <8s latency.

2. **Phase 2: OpenCode Coding & Tool-Use Shootout**
   - Benchmark `poolside/laguna-s-2.1` vs `meituan/longcat-2.0` vs `kwaipilot/kat-coder-air-v2.5` on Probe B8 (Tool Use) and B7 (Decomposition).
   - *Target:* Verify parameter precision, lack of hallucinated MCP arguments, and patch clean-rate.

3. **Phase 3: Long-Context Multi-Doc Audit**
   - Benchmark `minimax/minimax-m3` on Probe B6 (30k–60k needle recall test).
   - *Target:* Confirm 100% precision on configuration path extraction without latency degradation.

---

## 4. Integration into Model Ops Governance

Upon completion of empirical benchmarking via the standard evaluation protocol (`eval-protocol.md`), results should be logged directly into `experiment-log.md`. Qualifying models meeting the score thresholds (R2 ≥ 4.5, R1 ≥ 4.7) will be promoted into `routing-matrix.md` to continuously drive down cost and improve latency across Hermes and OpenCode.

## 5. Muse Glimmer 30B Evaluation Result (2026-08-27)

### Evidence
- Model: `meta/muse-glimmer-30b`, OpenRouter route targeting DeepInfra `deepinfra/bf16`; verified context window 131,072 tokens.
- Evaluation artifacts: `/tmp/muse-glimmer-30b-summary.md` and `/tmp/muse-glimmer-real/eval_meta_muse-glimmer-30b.json`.
- Probes captured: B2, B3, B4, B5, and B8. This was a single captured run per probe, so it is qualification evidence rather than repeated-run production validation.
- Aggregate: 4.52/5.0, 84% assertion pass rate, 0.29s average latency, and $0.00 recorded evaluation cost. The verified provider rate card is $0.30/M input and $1.20/M output; do not treat the recorded zero as a guaranteed production price.

### Qualification decision
- **Promote to R2 triage/extraction fast-track:** B2, B4, B5, and B8 each scored 5.0/5 with 100% assertion passes and sub-second latency (0.21–0.35s). This supports bounded extraction, triage JSON, audit synthesis, and structured tool-call drafting.
- **Do not promote to R1:** B3 scored 2.58/5 and passed 1/5 assertions because the model returned empty content. It failed canonical sections, bold-label syntax, required citations, and task-owner preservation. The failure is operationally critical for vault account-note drafting.
- **Failure boundary:** No canonical vault mutations, unattended scheduled jobs, or customer-facing final outputs. Keep a verifier and the existing fallback ladder in place; any empty output or schema/assertion failure must escalate.

### Comparative interpretation
Muse Glimmer is materially faster than the existing documented R2 alternatives in this captured run, but the comparison is not like-for-like repeated-run evidence: prior Laguna S 2.1, LongCat 2.0, and Qwen 3.7 Flash figures come from different tasks and benchmark batches. Its current advantage is therefore bounded latency and clean target-probe behavior, not a claim of overall superiority. Laguna remains the established R1/OpenCode specialist, LongCat remains the deeper architectural/tool-workflow specialist, Qwen remains a validated R2 alternative, and GPT-5.4 remains the frontier fallback.
