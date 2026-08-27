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
| `kwaipilot/kat-coder-air-v2.5`    | Kwaipilot       |  262,144 (256k)  |       $0.150        |      $0.600       | OpenCode Light Coding & Script Sweeps    | Fast coding MoE tuned for automated issue resolution and git workflows; competitive pricing.                  | Focused on code/diff generation; not suitable for CS tone/narrative.       |
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
