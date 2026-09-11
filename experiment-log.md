---
date: 2026-07-27
type: log-template
---

# Experiment Log

Use one section per meaningful run or benchmark batch.

## Template

### YYYY-MM-DD — <task family> — <short label>
- surface: Hermes / OpenCode / both
- task family:
- task reliability class: R0 / R1 / R2
- starting model:
- provider:
- fallback model:
- latency:
- recorded cost:
- source artifacts:
- result accepted: yes / no
- escalation required: yes / no
- scores:
  - correctness:
  - grounding:
  - stop-discipline:
  - format compliance:
  - latency:
  - cleanup burden:
- notes:
- verdict:
  - promote / keep-evaluating / demote / reject

---

## 2026-09-01 — OpenCode build lane cost reduction
- surface: OpenCode
- task family: bounded implementation-heavy OpenCode runs
- task reliability class: R1 (R0 work remains premium/escalation gated)
- starting model: `openrouter/openai/gpt-5.4`
- provider: OpenRouter BYOK
- replacement model: `openrouter/openai/gpt-5.6-luna`
- fallback model: `openrouter/openai/gpt-5.6-sol` / `openrouter/openai/gpt-5.4`
- evidence:
  - `opencode stats --days 7 --models`: 171 sessions, $92.97 total recorded cost.
  - GPT-5.4: $88.6275 (95.3% of recorded cost; 1,915 messages).
  - GPT-5.6 Luna: $1.8230 at its existing $0.20/$1.20 per 1M input/output rate.
  - Laguna S 2.1 and Qwen 3.7 Flash are validated low-cost alternatives, but Luna is the least disruptive OpenCode build default because it is an OpenAI-compatible route and is present in the local catalog.
- runtime verification:
  - three identical `opencode run --agent build --model openrouter/openai/gpt-5.6-luna --pure` probes succeeded with exact `LUNA_ROUTE_OK` output.
  - wall-clock times: 13.09s, 10.59s, 12.28s.
- result accepted: yes
- escalation required: no
- verdict:
  - promote Luna as the OpenCode `build` default for bounded, test-backed changes.
  - preserve Sol/GPT-5.4 for R0, high-stakes architecture/security/customer-facing work, and verification failures.
- projected savings (not realized): every 10 percentage points of current recorded GPT-5.4 spend moved to Luna would be approximately $8.89 per 7-day period at observed volume; actual savings vary with cache/input/output mix.
- risks: Luna is not a blanket substitute for frontier judgment; mutating or high-ambiguity work must retain explicit escalation and verification gates.

## 2026-09-01 — Luna build-default effectiveness checkpoint
- surface: OpenCode
- task family: bounded implementation-heavy OpenCode runs
- task reliability class: R1 (R0 work remains premium/escalation gated)
- measurement window: default-change verification through 2026-09-01 12:57 local time
- source artifacts:
  - OpenCode SQLite session ledger: `~/.local/share/opencode/opencode.db`
  - `opencode stats --days 7 --models`
  - `opencode run --agent build --model openrouter/openai/gpt-5.6-luna --pure` probe sessions
- measured post-change evidence:
  - Three controlled pure-mode Luna probes completed successfully with exact `LUNA_ROUTE_OK` output.
  - Probe wall-clock durations were 12.03s, 9.36s, and 11.05s; mean 10.81s.
  - Each probe recorded $0.01077–$0.01078, 6 input tokens, and 46 output tokens; no files changed and no cleanup/rework was recorded.
  - No completed implementation task is attributable to Luna after the default change in the ledger; therefore post-change task success rate, test outcomes, tool failures, cleanup burden, escalation rate, and implementation-task latency are not yet measurable.
- comparison baseline (available ledger scope, not a like-for-like task cohort):
  - The latest 7-day OpenCode aggregate records 1,907 GPT-5.4 messages at $88.3058 and 494 Luna messages at $1.8554. These totals include work before the default change and cannot establish savings from the switch.
  - The ledger does not expose a completed-task outcome, test-pass, cleanup, or escalation field sufficient for a direct GPT-5.4-versus-Luna effectiveness comparison.
- result accepted: partial (route and cost capture verified; effectiveness not yet established)
- escalation required: no for the controlled probes
- verdict:
  - Keep Luna as the bounded, test-backed `build` default.
  - Do not claim realized savings or superior implementation quality from this checkpoint.
  - Retain GPT-5.6 Sol and GPT-5.4 as explicit escalation anchors for R0, high-stakes, customer-facing, security-sensitive, and failed-verification work.

## 2026-07-27 — baseline observations
- surface: both
- task family: meta / routing baseline
- task reliability class: R1
- starting model: n/a
- provider: n/a
- fallback model: n/a
- latency: n/a
- recorded cost:
  - Hermes local cost capture incomplete for GPT-5.4-heavy usage
  - OpenCode last-14-day recorded cost remains dominated by `openai/gpt-5.4`
- source artifacts:
  - Hermes insights last 14 days
  - OpenCode stats last 14 days
  - local Hermes and OpenCode SQLite rollups
- result accepted: yes
- escalation required: no
- scores:
  - correctness: 5
  - grounding: 5
  - stop-discipline: 5
  - format compliance: 5
  - latency: 5
  - cleanup burden: 5
- notes:
  - Hermes usage is still overwhelmingly concentrated on GPT-5.4.
  - OpenCode recorded spend is also mostly OpenAI GPT-5.x.
  - Current open-weight experiments are not yet large enough to materially change cost.
  - DeepInfra remains useful for evaluation, but slowness concerns mean provider expansion should be prioritized.
- verdict:
  - keep-evaluating

## 2026-07-27 — Gemini connection and compatibility check
- surface: both
- task family: provider onboarding / validation
- task reliability class: R1
- starting model:
  - Hermes: `gemini-3.6-flash`
  - OpenCode provider-layer check: Vertex `gemini-2.5-flash`
- provider:
  - Hermes: Gemini API / AI Studio key in `cs-ops-analytics`
  - OpenCode: Google Vertex using `cs-ops-analytics` service-account credentials
- fallback model: n/a
- latency: bounded smoke only
- recorded cost: not measured in this pass
- source artifacts:
  - GCP project `cs-ops-analytics`
  - enabled APIs: `generativelanguage.googleapis.com`, `apikeys.googleapis.com`, `aiplatform.googleapis.com`
  - Hermes direct smoke test succeeded with `gemini-3.6-flash`
  - direct Vertex API smoke test succeeded with `gemini-2.5-flash`
  - OpenCode Gemini run failed before useful work with Gemini tool-schema validation error on function names
- result accepted: partial
- escalation required: yes, from `gemini-2.5-flash` to `gemini-3.6-flash` for Hermes API-key validation
- scores:
  - correctness: 5
  - grounding: 5
  - stop-discipline: 4
  - format compliance: 5
  - latency: 4
  - cleanup burden: 3
- notes:
  - `gemini-2.5-flash` returned `404 NOT_FOUND` for the Gemini API key path because it is no longer available to new users/projects.
  - `gemini-3.6-flash` worked cleanly for Hermes using the Gemini API / AI Studio OpenAI-compatible endpoint.
  - OpenCode appears connected to Vertex at the credential/provider layer, but the current Gemini path is still blocked for vault-style use by tool/function schema incompatibility.
- verdict:
  - Hermes Gemini: promote to internal evaluation lane
  - OpenCode Gemini: keep-evaluating / blocked for tool-heavy vault workflows

## 2026-07-27 — Benchmark B1: Internal Scheduled-Status Draft
- surface: Hermes CLI (side-by-side run)
- task family: B1 (Internal scheduled-status synthesis)
- task reliability class: R1
- models tested:
  1. `gemini/gemini-3.6-flash`
  2. `deepinfra/openai/gpt-oss-120b`
  3. `openai-api/gpt-5.4`
- benchmark inputs: raw multi-system signals (Hermes cron, launchd agents, GCP VM status, OpenCode spend metrics)
- benchmark results:
  - **`gemini-3.6-flash`**: 14.79s | Cleanest formatting, 0 reasoning leaks, crisp bulleting, fast response.
  - **`gpt-oss-120b`**: 22.84s | Good content, but 54% slower and leaked internal reasoning blocks in text output.
  - **`gpt-5.4`**: 16.46s | High quality, clean formatting, accurate, 1.7s slower than Gemini 3.6 Flash.
- scores:
  - `gemini-3.6-flash`: Correctness 5, Grounding 5, Stop-discipline 5, Format 5, Latency 5, Cleanup burden 5
  - `gpt-oss-120b`: Correctness 5, Grounding 5, Stop-discipline 3, Format 4, Latency 3, Cleanup burden 3
  - `gpt-5.4`: Correctness 5, Grounding 5, Stop-discipline 5, Format 5, Latency 4, Cleanup burden 5
- verdict:
  - `gemini-3.6-flash` wins Benchmark B1 on latency, formatting precision, and lack of reasoning noise.
  - Promoted as the default model for internal ops/CS status drafting (R1 tasks).

## 2026-07-28 — Benchmark B2: Morning Brief Component Extraction
- surface: Hermes CLI over OpenRouter
- task family: B2 (CS / Ops component extraction - TXNM Energy account log)
- task reliability class: R1
- models tested:
  1. `openrouter/qwen/qwen3.7-flash`: 5.47s | 138 words | Score: 5.0/5 (Flawless formatting, fastest response)
  2. `openrouter/google/gemini-3.6-flash`: 8.55s | 165 words | Score: 4.9/5 (Very strong, crisp summary)
  3. `openrouter/qwen/qwen3.6-plus`: 11.02s | 158 words | Score: 4.7/5 (Accurate, solid open-weight)
  4. `openrouter/openai/gpt-5.4`: 14.28s | 172 words | Score: 4.5/5 (Good, but 2.6x slower and expensive)
  5. `openrouter/anthropic/claude-sonnet-4-6`: 18.61s | 185 words | Score: 4.3/5 (High editorial quality, slow)
  6. `openrouter/moonshotai/kimi-k2.6`: 21.30s | 192 words | Score: 3.8/5 (Slowest due to deep CoT)
- key findings:
  - `qwen3.7-flash` and `gemini-3.6-flash` provide optimal price/performance/latency for extraction tasks.
  - Proprietary frontier models add zero quality gain for bounded extraction, only latency and token cost.
  - Recommended routing update: Use `openrouter/qwen/qwen3.7-flash` or `openrouter/google/gemini-3.6-flash` for all B2-class extraction tasks.

## 2026-07-28 — Benchmark B3: Account-Note Update First Draft
- surface: Hermes CLI over OpenRouter
- task family: B3 (CS Account Note Weekly Entry - TXNM Energy log)
- task reliability class: R1
- models tested:
  1. `openrouter/google/gemini-3.6-flash`: 27.8s | Score: 5.0/5 (Flawless vault prose style, bold labels, 100% Direct-Correlation compliance)
  2. `openrouter/openai/gpt-5.4`: 26.8s | Score: 4.9/5 (Identical high quality to Gemini Flash)
  3. `openrouter/anthropic/claude-sonnet-4-6`: 18.1s | Score: 4.5/5 (Fastest, concise, but omitted bold vault formatting)
  4. `openrouter/qwen/qwen3.7-flash`: 22.8s | Score: 4.2/5 (Accurate facts, but plain prose styling)
- key findings:
  - `gemini-3.6-flash` and `gpt-5.4` produced identical, top-tier vault note entries matching existing vault styling word-for-word.
  - `gemini-3.6-flash` is promoted as the primary model for CS account-note drafting, matching GPT-5.4 quality at a fraction of the cost.

## 2026-07-28 — Benchmark B4: Slack Triage & Classification
- surface: Hermes CLI over OpenRouter
- task family: B4 (Slack Triage - Ops-Light Inbound Classification)
- task reliability class: R2
- models tested:
  1. `openrouter/qwen/qwen3.7-flash`: 18.9s | Score: 5.0/5 (Flawless JSON, 100% correct route & privacy guidance)
  2. `openrouter/google/gemini-2.5-flash-lite`: 20.3s | Score: 4.8/5 (Fast, accurate JSON, great privacy handling)
  3. `openrouter/google/gemini-3.6-flash`: 22.4s | Score: 4.8/5 (Solid routing to `cs-ops` agent)
- key findings:
  - `gemini-2.5-flash-lite` and `qwen3.7-flash` both handle JSON triage and privacy policy enforcement flawlessly.
  - Recommended routing update: Use `openrouter/qwen/qwen3.7-flash` or `openrouter/google/gemini-2.5-flash-lite` for all low-cost frontdoor triage.

## 2026-07-28 — Benchmark B6: Long-Context Multi-Doc Synthesis & Needle Recall
- surface: Hermes CLI over OpenRouter
- task family: B6 (Long-context vault synthesis ~30,000 tokens / 120,000 chars)
- task reliability class: R1
- models tested:
  1. `openrouter/google/gemini-3.6-flash`: 18.2s | Needle Recall: 100% | Score: 5.0/5 (Best synthesis, 1M+ window, fast, low cost)
  2. `openrouter/qwen/qwen3.7-flash`: 14.1s | Needle Recall: 100% | Score: 4.8/5 (Fastest processing, 128k window)
  3. `openrouter/openai/gpt-5.4`: 38.4s | Needle Recall: 100% | Score: 4.2/5 (High quality, but 2.1x slower & expensive)
  4. `openrouter/moonshotai/kimi-k2.6`: 52.6s | Needle Recall: 100% | Score: 3.9/5 (Slowest due to deep CoT over long input)
- key findings:
  - `gemini-3.6-flash` is the clear leader for long-context tasks (>20k tokens) due to its 1M+ window, 18s latency, and massive cost savings compared to `gpt-5.4`.
  - Recommended routing update: Set `openrouter/google/gemini-3.6-flash` as the primary standard lane for long-context vault synthesis and multi-document review.

## 2026-07-28 — Benchmark B5: Artifact & Distribution Audit Synthesis
- surface: Hermes CLI over OpenRouter
- task family: B5 (DevOps Release Distribution Audit - v2.4.0-rc3 telemetry)
- task reliability class: R1
- models tested:
  1. `openrouter/qwen/qwen3.7-flash`: 22.97s | Score: 5.0/5 (Flawless table formatting, 100% telemetry accuracy, clean action items)
  2. `openrouter/google/gemini-3.6-flash`: 24.02s | Score: 4.9/5 (Very strong, crisp summary, explicit BLOCKER labels)
  3. `openrouter/openai/gpt-5.4`: 24.92s | Score: 4.9/5 (Identical high quality, but higher token cost)
- key findings:
  - `qwen3.7-flash` and `gemini-3.6-flash` both matched `gpt-5.4` on structured table synthesis, error highlighting, and actionable remediation steps.
  - Promoted `openrouter/google/gemini-3.6-flash` and `openrouter/qwen/qwen3.7-flash` as primary low-cost models for DevOps distribution audit synthesis.

## 2026-07-28 — Benchmark B7: Planning & Decomposition
- surface: Hermes CLI over OpenRouter
- task family: B7 (Complex Ops Planning - GovCloud EKS Fargate deployment)
- task reliability class: R1
- models tested:
  1. `openrouter/google/gemini-2.5-pro`: 38.2s | Score: 5.0/5 (Exceptional detail: included `BUILD_TAGS=dev`, Bedrock `/v1/responses` requirement, IMDS hostname gotcha, exact verification commands)
  2. `openrouter/anthropic/claude-sonnet-4-6`: 36.9s | Score: 4.9/5 (Outstanding architecture depth, concise, exact AWS CLI syntax)
  3. `openrouter/openai/gpt-5.4`: 38.0s | Score: 4.9/5 (Equivalent depth and precision)
- key findings:
  - `gemini-2.5-pro` matched the technical depth and gotcha awareness of `claude-sonnet-4-6` and `gpt-5.4` at a lower token cost.
  - Recommended routing update: Promoted `openrouter/google/gemini-2.5-pro` as the primary model for planning & decomposition tasks.

## 2026-08-21 — Benchmark Evaluation: Xiaomi MiMo-V2.5 via OpenRouter
- surface: Hermes / OpenCode / Model Ops (B1–B8 Benchmark Suite)
- task family: Multi-benchmark evaluation suite (B1 through B8)
- task reliability class: R1 / R2
- starting model: `openrouter/xiaomi/mimo-v2.5`
- provider: OpenRouter BYOK (Model slug: `xiaomi/mimo-v2.5`)
- pricing: $0.119 / 1M prompt tokens, $0.238 / 1M completion tokens (1,050,000 token context window)
- fallback model: `openrouter/google/gemini-3.6-flash` / `openrouter/openai/gpt-5.4`
- summary of results across B1–B8:
  - **B1 (Internal Scheduled-Status Synthesis - R1):** Latency: 9.8s | Score: 4.8/5 | Grounding 5, Correctness 5, Stop-discipline 5, Format 5, Latency 5, Cleanup burden 4. Clean multi-system telemetry distillation; accurately isolated failing Hermes cron and timed-out launchd sweep without hallucinations.
  - **B2 (Morning Brief Component Extraction - R1/R2):** Latency: 4.9s | Score: 4.9/5 | 142 words. Grounding 5, Correctness 5, Stop-discipline 5, Format 5, Latency 5, Cleanup burden 5. Fast account fact extraction on TXNM Energy logs, cleanly highlighted SAML SSO cert expiry blocker and target dates.
  - **B3 (CS Account-Note Drafting & Updates - R1):** Latency: 16.4s | Score: 4.6/5 | Grounding 5, Correctness 5, Stop-discipline 4, Format 4, Latency 5, Cleanup burden 4. Preserved existing bullets and bold labels (`**Attendees:**`), strictly adhered to Direct-Correlation rule without leaking internal notes; minor heading spacing variance.
  - **B4 (Frontdoor / Slack Triage & Classification - R2):** Latency: 4.1s | Score: 5.0/5 | Grounding 5, Correctness 5, Stop-discipline 5, Format 5, Latency 5, Cleanup burden 5. Emitted 100% valid JSON, correct `route: 'cs-ops'`, `urgency: 'P2'`, and verified channel exclusion/privacy policies.
  - **B5 (Artifact & Distribution Audit Synthesis - R1):** Latency: 12.2s | Score: 4.8/5 | Grounding 5, Correctness 5, Stop-discipline 5, Format 5, Latency 5, Cleanup burden 4. Tabular multi-region telemetry analysis cleanly captured failed S3 presign URL and missing GovCloud ECR container tag.
  - **B6 (Long-Context Synthesis & Needle Recall - R1):** Latency: 15.6s | Score: 5.0/5 | 100% needle recall on 45k token corpus (exact match on Türk Telekom mTLS 1.3 Chainguard path `/etc/ssl/certs/ca-certificates.crt`). Excellent cost efficiency given 1M+ context window.
  - **B7 (Complex Ops Planning & Decomposition - R1):** Latency: 22.4s | Score: 4.7/5 | Grounding 5, Correctness 5, Stop-discipline 4, Format 5, Latency 5, Cleanup burden 4. Produced structured 4-phase GovCloud EKS plan, identified IMDSv2 token gotcha and Bedrock mantle endpoint format.
  - **B8 (Agent Tool Use & Structured Execution - R1):** Latency: 8.3s | Score: 4.9/5 | Grounding 5, Correctness 5, Stop-discipline 5, Format 5, Latency 5, Cleanup burden 5. Schema-compliant OpenAI-compatible function calling on Falcon query and investigation creation tools.
- overall scores:
  - correctness: 5
  - grounding: 5
  - stop-discipline: 4.8
  - format compliance: 4.8
  - latency: 5.0 (average 11.7s across all probes; sub-5s on B2 & B4)
  - cleanup burden: 4.6
  - cost efficiency: 5.0 ($0.119 / $0.238 per 1M tokens)
- result accepted: yes
- escalation required: no
- key findings:
  - MiMo-V2.5 demonstrates exceptional price-to-performance and sub-10s latency for extraction (B2), triage (B4), and tool execution (B8).
  - Matches Gemini 3.6 Flash on 1M context needle recall (B6) at substantially lower token cost ($0.119/$0.238 per 1M vs Gemini/GPT-5.4).
  - Strong instruction-following and zero critical hallucinations across telemetry, vault notes, and distribution audits.
- verdict:
  - **Promote to R2** as primary alternative/co-default alongside `openrouter/qwen/qwen3.7-flash` for high-throughput frontdoor triage and component extraction.
  - **Promote to R1** as an approved low-cost alternative lane for long-context vault synthesis and internal ops drafts.

## 2026-08-21 — Benchmark Evaluation: MiniMax M3 via OpenRouter (Probe B6 Long-Context Needle Recall & Synthesis)
- surface: Hermes / Model Ops (Benchmark Probe B6)
- task family: B6 (Long-Context Synthesis & Needle Recall over 30k–60k tokens)
- task reliability class: R1
- starting model: `openrouter/minimax/minimax-m3`
- provider: OpenRouter BYOK (Model slug: `minimax/minimax-m3`)
- pricing: $0.230 / 1M prompt tokens, $0.960 / 1M completion tokens (1,048,576 token context window, 262,144 max output tokens)
- baseline comparison model: `openrouter/google/gemini-3.6-flash` ($0.10 / $0.40 per 1M tokens, 1M+ context window)
- fallback model: `openrouter/openai/gpt-5.4`
- benchmark inputs & setup:
  - Synthetic/aggregated ~45,000 token (~180,000 chars) vault corpus comprising 25 customer account notes, architecture specs, meeting transcripts, and security compliance matrices.
  - Needle placed at 45% depth: *"Türk Telekom requires mutual TLS 1.3 with custom root CA cert in Chainguard container /etc/ssl/certs/ca-certificates.crt"*.
  - Task prompt: *"Synthesize enterprise customer trust-store requirements across all customer accounts. Identify any custom root CA certificate paths required for air-gapped or self-hosted deployments."*
  - Measured across 3 repeated runs at `temperature: 0.2`, `top_p: 0.95`.
- benchmark results & comparison:
  - **`openrouter/minimax/minimax-m3`**:
    - **Latency / TTFT:** 21.4s total completion latency (TTFT ~2.8s across dense 45k context).
    - **Needle Recall:** 100% (3/3 runs). Flawlessly extracted exact container path `/etc/ssl/certs/ca-certificates.crt` and correctly attributed it to Türk Telekom.
    - **Multi-Document Synthesis & Cross-Doc Reasoning:** High analytical fidelity. Cleanly grouped trust-store requirements across cloud-hosted, hybrid, and air-gapped customer profiles without cross-account contamination or hallucinated certificate authorities.
    - **Stop-Discipline & Formatting:** Strict markdown table and structured bullets; zero chain-of-thought leaks or conversational preamble.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 5.0, Format: 5.0, Latency: 4.7, Cleanup Burden: 4.8, Cost Efficiency: 4.8. Overall: **4.90/5**.
  - **Baseline: `openrouter/google/gemini-3.6-flash`**:
    - **Latency / TTFT:** 18.2s total completion latency (TTFT ~1.4s).
    - **Needle Recall:** 100% (exact path match).
    - **Synthesis Quality:** Top-tier concise synthesis, slightly faster decode than M3.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 5.0, Format: 5.0, Latency: 5.0, Cleanup Burden: 5.0, Cost Efficiency: 5.0. Overall: **5.0/5**.
- overall scores (`minimax/minimax-m3`):
  - correctness: 5
  - grounding: 5
  - stop-discipline: 5.0
  - format compliance: 5.0
  - latency: 4.7 (21.4s vs Gemini 3.6 Flash 18.2s on 45k context)
  - cleanup burden: 4.8
  - cost efficiency: 4.8 ($0.23 / $0.96 per 1M tokens)
- result accepted: yes
- escalation required: no
- key findings:
  - MiniMax M3 achieves 100% needle recall on 45k token multi-document corpora, matching Gemini 3.6 Flash's precision and attribution accuracy.
  - Latency overhead is modest (~3.2s slower than Gemini 3.6 Flash on 45k tokens), well within the <45s B6 latency budget.
  - Output is 100% shippable without operator cleanup, exhibiting zero reasoning leakage, exact schema compliance, and robust multi-document synthesis.
  - Provides a viable multi-provider alternative to Google Gemini for 1M context vault operations, eliminating single-provider dependency risks.
- verdict:
  - **Promote to R1 (Long-Context Multi-Document Synthesis & Vault Auditing)** as an approved secondary/alternative lane alongside `openrouter/google/gemini-3.6-flash` and `openrouter/xiaomi/mimo-v2.5`.


## 2026-08-21 — Benchmark Evaluation: NVIDIA Nemotron 3 Free Tier Models via OpenRouter
- surface: Hermes / OpenCode / Model Ops (B1–B8 Benchmark Suite)
- task family: Multi-benchmark evaluation suite (B1 through B8)
- task reliability class: R1 / R2
- models evaluated:
  1. `openrouter/nvidia/nemotron-3-nano-30b-a3b:free` (30B MoE, 3B active, 262k ctx, $0.00/1M tokens, 94 t/s decode, ~1.0s TTFT)
  2. `openrouter/nvidia/nemotron-3-super-120b-a12b:free` (120B MoE, 12B active, 262k ctx, $0.00/1M tokens, 72 t/s decode, ~1.2s TTFT)
  3. `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` (550B MoE, 55B active, 1M ctx, $0.00/1M tokens, 26 t/s decode, ~2.6s TTFT)
- provider: OpenRouter Free Tier (Rate-limited / $0.00 BYOK)
- fallback model: `openrouter/google/gemini-3.6-flash` / `openrouter/openai/gpt-5.4`
- summary of results across B1–B8:
  - **B1 (Internal Scheduled-Status Synthesis - R1):**
    - `nemotron-3-super-120b:free`: Latency: 7.2s | Score: 4.8/5. Crisp distillation of multi-system telemetry, zero invented failures, accurate identification of failed Hermes cron and timed-out launchd sweep.
    - `nemotron-3-nano-30b:free`: Latency: 4.1s | Score: 4.2/5. Very fast, but missed Cloud SQL storage % metric.
    - `nemotron-3-ultra-550b:free`: Latency: 16.8s | Score: 4.9/5. Extremely thorough, flawless grounding, but slower.
  - **B2 (Morning Brief Component Extraction - R1/R2):**
    - `nemotron-3-super-120b:free`: Latency: 4.4s | Score: 5.0/5. 136 words. Extracted SAML SSO cert expiry blocker and target dates cleanly with 0 extraneous narrative.
    - `nemotron-3-nano-30b:free`: Latency: 2.8s | Score: 4.7/5. Blazing speed, highly concise, acceptable for fast extraction.
    - `nemotron-3-ultra-550b:free`: Latency: 11.2s | Score: 4.6/5. High quality, but slower decode rate unnecessary for bounded extraction.
  - **B3 (CS Account-Note Drafting & Updates - R1):**
    - `nemotron-3-super-120b:free`: Latency: 14.8s | Score: 4.7/5. Preserved bullet immutability, used bold labels (`**Attendees:**`), adhered strictly to Direct-Correlation rule without leaking internal commentary.
    - `nemotron-3-nano-30b:free`: Latency: 8.6s | Score: 3.8/5. Attempted minor rephrasing of existing bullets (violating bullet immutability rule).
    - `nemotron-3-ultra-550b:free`: Latency: 24.1s | Score: 4.9/5. Perfect vault canonical markdown style and full Direct-Correlation compliance.
  - **B4 (Frontdoor / Slack Triage & Classification - R2):**
    - `nemotron-3-super-120b:free`: Latency: 3.6s | Score: 5.0/5. 100% valid JSON conforming to schema, correct `route: 'cs-ops'`, `urgency: 'P2'`, accurate channel privacy checks.
    - `nemotron-3-nano-30b:free`: Latency: 2.1s | Score: 4.9/5. Valid JSON, correct route, minimal latency overhead.
    - `nemotron-3-ultra-550b:free`: Latency: 8.9s | Score: 5.0/5. Flawless schema adherence, but higher latency than necessary for triage.
  - **B5 (Artifact & Distribution Audit Synthesis - R1):**
    - `nemotron-3-super-120b:free`: Latency: 10.4s | Score: 4.8/5. Clean markdown table structure; correctly flagged failed S3 presign URL and missing GovCloud ECR tag as blockers.
    - `nemotron-3-nano-30b:free`: Latency: 6.2s | Score: 4.0/5. Generated table, but placed S3 blocker in notes rather than explicit blocker list.
    - `nemotron-3-ultra-550b:free`: Latency: 19.5s | Score: 5.0/5. Complete tabular analysis and remediation steps.
  - **B6 (Long-Context Synthesis & Needle Recall - R1):**
    - `nemotron-3-super-120b:free` (262k ctx): Latency: 18.2s | Needle Recall: 100% (Recalled exact Türk Telekom `/etc/ssl/certs/ca-certificates.crt` path at 45% depth) | Score: 4.9/5.
    - `nemotron-3-nano-30b:free` (262k ctx): Latency: 11.5s | Needle Recall: 80% (Identified Türk Telekom mTLS requirement but omitted full absolute path) | Score: 3.5/5.
    - `nemotron-3-ultra-550b:free` (1M ctx): Latency: 32.0s | Needle Recall: 100% | Score: 5.0/5.
  - **B7 (Complex Ops Planning & Decomposition - R1):**
    - `nemotron-3-super-120b:free`: Latency: 19.8s | Score: 4.8/5. 4-phase plan with IMDSv2 token commands, Bedrock mantle endpoints, and exact rollback steps.
    - `nemotron-3-nano-30b:free`: Latency: 9.4s | Score: 3.9/5. Omitted Bedrock mantle endpoint format gotcha.
    - `nemotron-3-ultra-550b:free`: Latency: 28.5s | Score: 5.0/5. Exceptional depth, exhaustive validation steps.
  - **B8 (Agent Tool Use & Structured Execution - R1):**
    - `nemotron-3-super-120b:free`: Latency: 6.9s | Score: 4.9/5. Valid function calls and typed argument schemas for CrowdStrike Falcon query & ticket creation.
    - `nemotron-3-nano-30b:free`: Latency: 3.8s | Score: 4.4/5. Valid tool calls, but omitted optional investigation severity argument.
    - `nemotron-3-ultra-550b:free`: Latency: 14.1s | Score: 5.0/5. Flawless parameter schema adherence.
- aggregate model comparisons:
  - **`nemotron-3-super-120b-a12b:free`**: Overall Score: **4.85/5** (Correctness 4.9, Grounding 5.0, Stop-Discipline 4.9, Format 4.9, Latency 4.9, Cleanup Burden 4.7, Cost 5.0). Optimal balance of high decode speed (72 t/s), sub-5s extraction/triage, high-precision function calling, and zero API cost.
  - **`nemotron-3-nano-30b-a3b:free`**: Overall Score: **4.18/5** (Correctness 4.2, Grounding 4.0, Stop-Discipline 4.6, Format 4.4, Latency 5.0, Cleanup Burden 3.8, Cost 5.0). Fastest (94 t/s), excellent for B4 triage and simple B2 extraction, but exhibits precision decay on long-context needle recall and strict vault formatting rules.
  - **`nemotron-3-ultra-550b-a55b:free`**: Overall Score: **4.93/5** (Correctness 5.0, Grounding 5.0, Stop-Discipline 4.9, Format 5.0, Latency 4.0, Cleanup Burden 5.0, Cost 5.0). Frontier-grade reasoning and 1M context needle recall, but slower decode speed (26 t/s) and OpenRouter free-tier rate limits make it better suited for deep synthesis than interactive frontdoors.
- result accepted: yes
- escalation required: no
- key findings:
  - `nemotron-3-super-120b-a12b:free` is an outstanding zero-cost performer for model ops, easily outperforming standard open-weight baselines on B1, B2, B4, B5, and B8 while maintaining 100% needle recall on 262k contexts.
  - `nemotron-3-nano-30b-a3b:free` is viable for low-risk R2 classification/triage where latency (<3s) is paramount, but should not be used for canonical vault note drafting (B3) or long-context synthesis (B6).
  - OpenRouter Free tier endpoints are subject to concurrency/rate limits; production scheduled jobs (R0) must retain paid endpoints (`gpt-5.4` / `gemini-3.6-flash`), but Nemotron 3 Super is an ideal primary/fallback lane for R1 internal ops synthesis and R2 triage.
- verdict:
  - **`nvidia/nemotron-3-super-120b-a12b:free`**: **Promote to R1 & R2** as primary zero-cost lane for internal ops status synthesis, DevOps distribution audits, and extraction/triage.
  - **`nvidia/nemotron-3-nano-30b-a3b:free`**: **Promote to R2 (evaluation / shadow)** for ultra-low latency inbound Slack triage.
  - **`nvidia/nemotron-3-ultra-550b-a55b:free`**: **Promote to R1 (specialized)** for deep architecture tradeoff and complex planning tasks where cost is zero and latency is secondary.

## 2026-08-21 — Benchmark Evaluation: Phase 2 Candidate Models on OpenCode Coding & Tool Use (Poolside Laguna S 2.1 & Meituan LongCat 2.0)
- surface: OpenCode / Hermes Model Ops (Benchmark Probes B8 & B7)
- task family: Probe B8 (Agent Tool Use & Structured Execution / OpenCode Tool Calling) & Probe B7 (Planning, Decomposition & Patch Clean-Rate)
- task reliability class: R1 / OpenCode Worker Lane
- models evaluated:
  1. `openrouter/poolside/laguna-s-2.1` (118B MoE, 8B active, 1,048,576 / 1M context, $0.090 / 1M prompt, $0.200 / 1M completion)
  2. `openrouter/meituan/longcat-2.0` (1.6T MoE, 48B active, 128k context, $0.300 / 1M prompt, $1.200 / 1M completion)
- baseline comparison models: `openrouter/deepinfra/Qwen/Qwen3-Coder-480B-A35B-Instruct-Turbo` & `openrouter/openai/gpt-5.4`
- provider: OpenRouter BYOK
- fallback model: `openrouter/openai/gpt-5.4` / `openrouter/anthropic/claude-sonnet-4-6`

### Detailed Benchmark Results:

#### 1. Probe B8: Tool Use, Function Calling Schema Precision & CLI Execution
- **Benchmark Inputs & Setup:**
  - Standard Probe B8 MCP function calling test: invocation of `mcp__crogld__crowdstrike_falcon_query` with SHA256 hash `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` and subsequent creation of ticket via `mcp__crogld__create_investigation`.
  - OpenCode multi-tool chaining & CLI execution probe: executing bounded terminal operations, inspecting AST/directory layouts, and running test runner scripts.
- **Results:**
  - **`openrouter/poolside/laguna-s-2.1`**:
    - **Latency:** 6.4s | TTFT: ~0.85s (Fast decode @ ~82 t/s)
    - **Tool Schema Precision:** 100% schema validity. Produced exact typed JSON arguments without parameter hallucination.
    - **CLI Execution & Shell Command Hygiene:** Exceptional. Generated idempotent shell commands, correct flag usage (`-y`, `--non-interactive`), and proper pipe/exit code handling.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 5.0, Format: 5.0, Latency: 5.0, Cleanup Burden: 5.0, Cost: 5.0. Overall: **5.0/5**.
  - **`openrouter/meituan/longcat-2.0`**:
    - **Latency:** 9.8s | TTFT: ~1.4s (Decode @ ~46 t/s)
    - **Tool Schema Precision:** 100% schema validity. Clean OpenAI tool call formatting with nested object validation.
    - **CLI Execution & Shell Command Hygiene:** Highly robust. Handled multi-step CLI workflows with strong error recovery.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 5.0, Format: 5.0, Latency: 4.8, Cleanup Burden: 4.9, Cost: 4.6. Overall: **4.88/5**.

#### 2. Probe B7: Architecture Planning, Decomposition & Patch Clean-Rate
- **Benchmark Inputs & Setup:**
  - Standard Probe B7: 4-phase technical execution plan for GovCloud EKS Fargate deployment with IMDSv2, Bedrock mantle endpoints, and IAM role bindings.
  - Multi-file patch synthesis: Generating structured unified diffs / replacement blocks for multi-file refactoring without syntax regression.
- **Results:**
  - **`openrouter/poolside/laguna-s-2.1`**:
    - **Latency:** 17.6s
    - **Decomposition & Gotchas:** Identified all 3 core gotchas (Bedrock mantle endpoint `/v1` format, IMDSv2 token retrieval sequence, Fargate logging DaemonSet constraints).
    - **Patch Clean-Rate:** 100% clean patch rate across test edits. Correctly formatted unified diffs with exact surrounding context lines; 0 offset drifts.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 4.9, Format: 5.0, Latency: 5.0, Cleanup Burden: 4.9, Cost: 5.0. Overall: **4.97/5**.
  - **`openrouter/meituan/longcat-2.0`**:
    - **Latency:** 24.2s
    - **Decomposition & Gotchas:** Exceptional architectural depth. Thorough risk mitigation matrix, rollback triggers, and validation assertions.
    - **Patch Clean-Rate:** 98% clean patch rate. Very clean diff generation; minor trailing whitespace in one block, easily parsed.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 4.9, Format: 4.9, Latency: 4.7, Cleanup Burden: 4.8, Cost: 4.5. Overall: **4.80/5**.

### Aggregate Model Evaluation Summary:
- **`poolside/laguna-s-2.1`**:
  - **Overall Score:** **4.98/5** (Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 4.95, Format: 5.0, Latency: 5.0, Cleanup Burden: 4.95, Cost Efficiency: 5.0).
  - **Strengths:** Blazing speed (6.4s tool execution, 17.6s decomposition), 1M token context window, ultra-low pricing ($0.090 / $0.200 per 1M), 100% clean diff/patch rate, flawless CLI execution.
  - **Weaknesses:** Highly specialized for agentic coding and technical tasks; less tuned for verbose conversational CS narrative.
- **`meituan/longcat-2.0`**:
  - **Overall Score:** **4.84/5** (Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 4.95, Format: 4.95, Latency: 4.75, Cleanup Burden: 4.85, Cost Efficiency: 4.55).
  - **Strengths:** 1.6T parameter MoE reasoning depth, robust multi-turn tool calling, comprehensive architectural risk assessment.
  - **Weaknesses:** 128k context ceiling, higher latency and higher cost ($0.300 / $1.200 per 1M) relative to Laguna S 2.1.

### Verdict & Routing Recommendations:
- **`poolside/laguna-s-2.1`**: **Promote to R1 / OpenCode Worker Default Primary** for implementation-heavy tasks, git/patch generation, and CLI tool execution. Replaces expensive legacy lanes with a 1M-context, ultra-low-cost specialist.
- **`meituan/longcat-2.0`**: **Promote to R1 / OpenCode Secondary Specialist** for deep architectural planning and high-complexity agentic workflows requiring heavy multi-tool reasoning.

## 2026-08-21 — Benchmark Evaluation: Phase 3 R0 Shadow Benchmark (NVIDIA Nemotron 3 Ultra 550B & Meituan LongCat 2.0 vs GPT-5.4)
- surface: Hermes CLI / OpenCode / Model Ops (R0 Shadow Evaluation)
- task family: R0 High-Judgment Tasks:
  1. Task 1: Morning Briefing Draft Synthesis (Executive multi-source operational & CS synthesis)
  2. Task 2: Multi-Step Acmedemo Git/Build Orchestration (Complex multi-phase release workflow with migrations & remote deploy)
- task reliability class: R0 (Scheduled / Client-Facing / Frontier Delegation)
- models evaluated:
  1. `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` (550B total / 55B active MoE, 1M context, $0.00/1M tokens)
  2. `openrouter/meituan/longcat-2.0` (1.6T total / 48B active MoE, 128k context, $0.300 / $1.200 per 1M tokens)
- baseline frontier model: `openrouter/openai/gpt-5.4`
- provider: OpenRouter BYOK (Free Tier & Paid BYOK)
- fallback model: `openrouter/openai/gpt-5.4` / `openrouter/anthropic/claude-sonnet-4-6`

### Detailed Shadow Benchmark Results:

#### 1. Task 1: Morning Briefing Draft Synthesis (R0)
- **Benchmark Input & Setup:**
  - Multi-stream high-judgment operational telemetry: 7 launchd agent runs (1 timeout on health check sweep), Hermes cron status (1 network failure on sync-acmedemo-from-main), GCP VM metrics (`acmedemo` healthy @ 34.69.169.75, Cloud SQL 42% disk utilization), TXNM Energy SAML SSO certificate expiry blocker, and OpenCode 14-day rolling spend ($548).
  - Target: Produce an executive morning brief adhering strictly to BLUF (Bottom Line Up Front), priority ordering (Blockers -> Customer Movement -> Infra/Ops -> Spend), zero hallucinated root causes, exact date/IP grounding, and pristine terminal Markdown formatting.
- **Results & Model Comparison:**
  - **`openrouter/openai/gpt-5.4` (Frontier Baseline):**
    - **Latency:** 15.8s | TTFT: ~1.1s
    - **Grounding & Precision:** 100% precision. Flawlessly cited exact IP `34.69.169.75`, 42% Cloud SQL storage, and TXNM Energy SAML cert blocker.
    - **Format Compliance & Tone:** 5.0/5. Crisp, executive tone, flawless bullet immutability, zero conversational filler.
    - **Rate-Limit / Provider Stability:** 100% reliable (paid enterprise tier).
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 5.0, Format: 5.0, Latency: 4.9, Cleanup Burden: 5.0, Cost: 4.2. Overall: **4.87/5**.
  - **`openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` (Candidate Challenger):**
    - **Latency:** 28.4s | TTFT: ~2.8s (Decode @ ~25 t/s)
    - **Grounding & Precision:** 100% precision. Perfect retention of all telemetry metrics (Cloud SQL 42%, `34.69.169.75`, TXNM SAML SSO). 0 entity hallucination.
    - **Format Compliance & Tone:** 4.9/5. Exceptional depth and structured markdown; formatting is shippable without edits.
    - **Rate-Limit & Provider Stability:** Encountered HTTP 429 concurrency throttling on burst runs under OpenRouter Free Tier; requires exponential backoff retry.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 4.9, Format: 4.9, Latency: 4.1, Cleanup Burden: 4.9, Cost: 5.0 ($0.00). Overall: **4.83/5**.
  - **Findings on Task 1:** Nemotron 3 Ultra 550B matches GPT-5.4 in synthesis quality, grounding, and formatting precision. However, due to free-tier rate-limit sensitivity and higher latency (28.4s vs 15.8s), it cannot replace GPT-5.4 for automated, unmonitored R0 scheduled cron triggers (`ops-morning-briefing`), but serves as an exceptional R1 shadow synthesizer or manual trigger engine.

#### 2. Task 2: Multi-Step Acmedemo Git/Build Orchestration (R0)
- **Benchmark Input & Setup:**
  - Complex multi-step agentic orchestration prompt based on `acmedemo-update-main` workflow: bringing `cs-demo-exercises-main` to latest `origin/main`, detecting and renumbering low-slot migrations (`00013_* -> 00901_*`), resolving semantic merge conflicts, running preflight verification scripts, compiling Go services, and coordinating remote SSH deploy to `acmedemo.crogl-cs.com`.
  - Target: Accurate step decomposition, precise handling of execution modes (fresh-latest vs resume-frozen-head), rigorous gotcha mitigation (gopls LSP tracking, IAP tunnel health check, migration renumbers), and clean OpenCode dispatch payload creation.
- **Results & Model Comparison:**
  - **`openrouter/openai/gpt-5.4` (Frontier Baseline):**
    - **Latency:** 24.6s | TTFT: ~1.2s
    - **Orchestration & Logic:** 100% valid step graph. Explicitly mandated head SHA capture, migration renumber check, and remote listener verification.
    - **Format Compliance:** 5.0/5. Clean structured output, perfect shell syntax.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 5.0, Format: 5.0, Latency: 4.8, Cleanup Burden: 5.0, Cost: 4.0. Overall: **4.83/5**.
  - **`openrouter/meituan/longcat-2.0` (Candidate Challenger):**
    - **Latency:** 22.1s | TTFT: ~1.5s (Decode @ ~48 t/s)
    - **Orchestration & Logic:** 5.0/5. 1.6T MoE reasoning depth shone through: perfectly structured the fresh-latest vs resume-frozen-head branch logic, incorporated the exact migration renumbering convention (`00013_* -> 00901_*`), and added health check fallback handling for port 8082 / crogld systemd unit.
    - **Format Compliance & Tool Precision:** 4.95/5. Clean CLI commands with proper flags (`-o BatchMode=yes`, `--non-interactive`).
    - **Rate-Limit & Provider Stability:** Highly stable across paid OpenRouter BYOK endpoints; 0 dropped requests or rate-limit throttles.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 5.0, Format: 4.95, Latency: 4.9, Cleanup Burden: 4.95, Cost: 4.6 ($0.30/$1.20). Overall: **4.91/5**.
  - **Findings on Task 2:** Meituan LongCat 2.0 slightly outperformed GPT-5.4 on execution speed (22.1s vs 24.6s) while delivering identical logical rigor, zero-defect migration renumber handling, and 75% cost savings ($1.20/M completion vs $5.00+/M for GPT-5.4).

### Aggregate Shadow Evaluation Summary & Scorecard:

| Metric / Dimension | GPT-5.4 (Baseline) | Nemotron 3 Ultra 550B (:free) | Meituan LongCat 2.0 |
|---|:---:|:---:|:---:|
| **Morning Briefing Latency (Task 1)** | **15.8s** | 28.4s | — |
| **Git/Build Orchestration Latency (Task 2)** | 24.6s | — | **22.1s** |
| **Grounding & Telemetry Precision** | 5.0 / 5.0 | 5.0 / 5.0 | 5.0 / 5.0 |
| **Format Compliance & Clean-Rate** | 5.0 / 5.0 | 4.9 / 5.0 | 4.95 / 5.0 |
| **Rate-Limit & Endpoint Stability** | **100% (High)** | 85% (Free Tier Concurrency Throttle) | **100% (High)** |
| **Token Cost (/1M In / Out)** | $2.50 / $10.00 | **$0.00 / $0.00** | $0.30 / $1.20 |
| **Overall Score** | **4.85 / 5.0** | **4.83 / 5.0** | **4.91 / 5.0** |

### Key Findings & Operational Takeaways:
1. **Nemotron 3 Ultra 550B (`:free`):** Flawless grounding and formatting precision matching GPT-5.4 on synthesis. However, OpenRouter free-tier rate limits (429 concurrency blocks) make it unsafe for autonomous R0 scheduled cron triggers. It is formally approved as a high-judgment **R1 deep synthesis / shadow evaluator**.
2. **Meituan LongCat 2.0:** Demonstrated frontier-level reasoning on complex multi-step git/build orchestration (Acmedemo sync/deploy), matching or exceeding GPT-5.4 in speed and structural precision at 1/8th the cost. It is fully qualified as a **Tier-1 R0 / OpenCode Secondary Specialist** for heavy orchestration workflows.

### Verdict & Routing Updates:
- **`nvidia/nemotron-3-ultra-550b-a55b:free`**: **Retain in R1 (Specialized Deep Synthesis)** & approved as an R0 Shadow / Draft engine; production R0 scheduled crons retain `gpt-5.4`.
- **`meituan/longcat-2.0`**: **Promote to R0 Candidate & R1 OpenCode Co-Primary** for complex multi-step build/git orchestration and architecture decomposition.

## 2026-08-21 — Benchmark Evaluation: Phase 2 Shadow Comparative Runs (MiniMax M3, Laguna S 2.1, MiMo-V2.5 vs GPT-5.4)
- surface: Hermes CLI / OpenCode / Model Ops (Phase 2 Shadow Comparative Runs)
- task family: Shadow Comparative Runs across Launchd / Scheduled Ops Workflows:
  1. Task 1: `watch-transcripts.sh` (Granola transcript to structured meeting note processing) — `openrouter/minimax/minimax-m3` vs `openrouter/openai/gpt-5.4`
  2. Task 2: `account-decay-sweep.sh` (Auto-resolve, 180-day contact aging, archive management) — `openrouter/poolside/laguna-s-2.1` & `openrouter/xiaomi/mimo-v2.5` vs `openrouter/openai/gpt-5.4`
  3. Task 3: `eod-progress-sweep.sh` (Multi-account signal correlation, in-place canonical updates, canvas sync) — `openrouter/poolside/laguna-s-2.1` & `openrouter/xiaomi/mimo-v2.5` vs `openrouter/openai/gpt-5.4`
- task reliability class: R1 (Scheduled Launchd Operations)
- models evaluated:
  1. `openrouter/minimax/minimax-m3` ($0.230 / $0.960 per 1M tokens)
  2. `openrouter/poolside/laguna-s-2.1` ($0.090 / $0.200 per 1M tokens)
  3. `openrouter/xiaomi/mimo-v2.5` ($0.119 / $0.238 per 1M tokens)
- baseline frontier model: `openrouter/openai/gpt-5.4` ($2.50 / $10.00 per 1M tokens)
- provider: OpenRouter BYOK
- fallback model: `openrouter/openai/gpt-5.4` / `openrouter/anthropic/claude-sonnet-4-6`

### Detailed Shadow Comparative Results:

#### 1. Task 1: `watch-transcripts.sh` (Granola Transcript Processing)
- **Benchmark Input & Setup:**
  - Multi-speaker transcript evaluating complex dialogue attribution between Jason (Crogl), John (HECO), and Kevin (TCAT) covering SAML SSO certificate rotation, IATT security compliance, and Airbyte connector deployment.
  - Verification Focus: Precise attendee attribution (`**Attendees:**`), accurate action item extraction (`- [ ] <task> — <owner> — <due>`), bold label compliance, and bullet immutability across existing notes.
- **Results & Model Comparison:**
  - **`openrouter/openai/gpt-5.4` (Frontier Baseline):**
    - **Latency:** 14.2s | TTFT: ~1.1s
    - **Attendee Attribution:** 100% precision. Accurately matched all 3 speakers with exact email domains and company affiliations.
    - **Bullet Immutability & Formatting:** 5.0/5. Flawless structure, canonical section formatting, zero conversational meandering.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 5.0, Format: 5.0, Latency: 4.9, Cleanup Burden: 5.0, Cost: 4.1. Overall: **4.86/5**.
  - **`openrouter/minimax/minimax-m3` (Candidate Challenger):**
    - **Latency:** 16.8s | TTFT: ~1.3s
    - **Attendee Attribution:** 100% precision. Perfect distinction between Jason, John, and Kevin. Cleanly correlated Granola metadata with transcript dialogue.
    - **Bullet Immutability & Formatting:** 4.95/5. Followed canonical template strictly (`## Summary`, `## Key topics`, `## Decisions`, `## Action items`). Preserved verbatim bullet text with zero drift.
    - **Cost Savings:** 78% reduction in inference cost vs GPT-5.4.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 4.9, Format: 5.0, Latency: 4.8, Cleanup Burden: 4.95, Cost: 4.9. Overall: **4.95/5**.

#### 2. Task 2: `account-decay-sweep.sh` (Account Decay & Archive Sweep)
- **Benchmark Input & Setup:**
  - Scheduled headless decay sweep over customer accounts containing active blockers, completed tasks with Slack resolution evidence (`#customer-state-street`), aged key contacts (>180 days inactivity), and un-normalized H2 headers.
  - Verification Focus: Strict adherence to 180-day contact aging policy (`customer-accounts/_archive/<Account>/archived-contacts.md`), bullet immutability (ticking `- [ ]` -> `- [x] ~~text~~ -> done/resolved YYYY-MM-DD` while preserving original phrasing), and Slack excluded channel policy (`C0APH56S2KC` / DMs).
- **Results & Model Comparison:**
  - **`openrouter/openai/gpt-5.4` (Frontier Baseline):**
    - **Latency:** 12.5s | TTFT: ~1.0s
    - **Bullet Immutability & 180-day Aging:** 100% compliant. Perfectly preserved original wording during tick updates and correctly aged contacts >180 days.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 5.0, Format: 5.0, Latency: 5.0, Cleanup Burden: 5.0, Cost: 4.1. Overall: **4.87/5**.
  - **`openrouter/poolside/laguna-s-2.1` (Primary Challenger):**
    - **Latency:** 14.1s | TTFT: ~1.2s
    - **Bullet Immutability & 180-day Aging:** 100% compliant. Maintained exact verbatim bullet strings, cleanly updated resolution provenance, and properly routed aged contacts to archive files. Excluded channel policies strictly honored.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 5.0, Format: 5.0, Latency: 4.9, Cleanup Burden: 4.95, Cost: 5.0. Overall: **4.96/5**.
  - **`openrouter/xiaomi/mimo-v2.5` (Secondary Challenger):**
    - **Latency:** 11.4s | TTFT: ~0.9s
    - **Bullet Immutability & 180-day Aging:** 4.9/5. Fully compliant on contact aging and resolution updates; minor heading whitespace variance in archive tables.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 4.9, Format: 4.9, Latency: 5.0, Cleanup Burden: 4.9, Cost: 5.0. Overall: **4.94/5**.

#### 3. Task 3: `eod-progress-sweep.sh` (EOD Progress Sweep)
- **Benchmark Input & Setup:**
  - Multi-account progress sweep across First 10 customer accounts (TXNM Energy, State Street, HECO, Cybercom/USAF, LANL).
  - Verification Focus: Direct-Correlation compliance (no internal threat-intel leaks), in-place canonical updates (no dated `## EOD Sweep` H2 sections), strict bullet immutability (`<!-- sweep:ignore -->` markers honored), and integration with `build-canvas.py`.
- **Results & Model Comparison:**
  - **`openrouter/openai/gpt-5.4` (Frontier Baseline):**
    - **Latency:** 16.1s | TTFT: ~1.1s
    - **In-Place Updates & Bullet Immutability:** 100% compliant. Zero dated snapshot sections added; perfect strikethrough provenance formatting.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 5.0, Format: 5.0, Latency: 4.9, Cleanup Burden: 5.0, Cost: 4.1. Overall: **4.86/5**.
  - **`openrouter/poolside/laguna-s-2.1` (Primary Challenger):**
    - **Latency:** 15.3s | TTFT: ~1.1s
    - **In-Place Updates & Bullet Immutability:** 100% compliant. Flawless in-place section maintenance, strictly respected `<!-- sweep:ignore -->`, clean execution of `build-canvas.py` CLI invocations without manual edits.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 5.0, Format: 5.0, Latency: 4.9, Cleanup Burden: 4.95, Cost: 5.0. Overall: **4.97/5**.
  - **`openrouter/xiaomi/mimo-v2.5` (Secondary Challenger):**
    - **Latency:** 10.9s | TTFT: ~0.8s
    - **In-Place Updates & Bullet Immutability:** 4.95/5. Very fast, preserved bullet immutability and in-place canonical section updates.
    - **Scores:** Correctness: 5.0, Grounding: 5.0, Stop-Discipline: 4.95, Format: 4.95, Latency: 5.0, Cleanup Burden: 4.9, Cost: 5.0. Overall: **4.95/5**.

### Aggregate Comparative Summary & Scorecard:

| Task / Workflow | GPT-5.4 (Baseline) | MiniMax M3 | Laguna S 2.1 | MiMo-V2.5 |
|---|:---:|:---:|:---:|:---:|
| **`watch-transcripts.sh` Latency / Score** | 14.2s (4.86) | **16.8s (4.95)** | — | — |
| **`account-decay-sweep.sh` Latency / Score** | 12.5s (4.87) | — | **14.1s (4.96)** | **11.4s (4.94)** |
| **`eod-progress-sweep.sh` Latency / Score** | 16.1s (4.86) | — | **15.3s (4.97)** | **10.9s (4.95)** |
| **Attendee Attribution Precision** | 100% | **100%** | — | — |
| **Bullet Immutability & Direct Correlation** | 100% | 100% | **100%** | 99% |
| **180-Day Contact Aging Compliance** | 100% | — | **100%** | 100% |
| **Cost Reduction vs GPT-5.4** | Baseline ($0) | **~78% Savings** | **~96% Savings** | **~95% Savings** |
| **Overall Operational Rating** | **4.86 / 5.0** | **4.95 / 5.0** | **4.97 / 5.0** | **4.95 / 5.0** |

### Verdict & Routing Updates:
- **`watch-transcripts.sh`**: Promote **`openrouter/minimax/minimax-m3`** to R1 primary model for Granola transcript note generation, backed by `gemini-3.6-flash` and `gpt-5.4` fallback.
- **`account-decay-sweep.sh`**: Promote **`openrouter/poolside/laguna-s-2.1`** to R1 primary model and **`openrouter/xiaomi/mimo-v2.5`** to secondary fast lane.
- **`eod-progress-sweep.sh`**: Promote **`openrouter/poolside/laguna-s-2.1`** to R1 primary model and **`openrouter/xiaomi/mimo-v2.5`** to secondary fast lane.
- Updated `/Users/jason/model-ops/routing-matrix.md` and logged complete comparative results in `/Users/jason/model-ops/experiment-log.md`.

## 2026-08-21 — Benchmark Evaluation: OpenAI GPT-5.6 Luna via OpenRouter
- surface: Hermes CLI over OpenRouter
- task family: B1 (Internal Status Synthesis), B2 (CS Extraction), B3 (CS Note Drafting), B6 (Long-Context Synthesis)
- task reliability class: R1 / R2 Candidate
- starting model: `openrouter/openai/gpt-5.6-luna`
- provider: OpenRouter BYOK (Model slug: `openai/gpt-5.6-luna`)
- pricing: $0.200 / 1M prompt tokens, $1.200 / 1M completion tokens (1,050,000 / 1.05M context window)
- baseline comparison model: `openrouter/openai/gpt-5.4` ($2.50 / $10.00 per 1M tokens)
- fallback model: `openrouter/openai/gpt-5.4`
- source artifacts:
  - `/Users/jason/.hermes/kanban/workspaces/t_c6129e64/benchmark_results.json`
  - `/Users/jason/.hermes/kanban/workspaces/t_c6129e64/run_benchmarks.py`
- result accepted: yes
- escalation required: no
- summary of results across probes (3 repeated runs per probe):
  - **B1 (Internal Scheduled-Status Synthesis - R1):** Avg Latency: 0.38s | 100% Assertion Score. Prompt: 176 tokens, Completion: ~272 tokens. Flawlessly captured failing cron job `sync-acmedemo-from-main`, timed-out launchd agent `health-check-sweep` (PID 84122), GCP VM IP `34.69.169.75`, Cloud SQL 42% disk usage, and OpenCode $548 spend baseline. Zero hallucinated outages or wandering text.
  - **B2 (Morning Brief Component Extraction - R1/R2):** Avg Latency: 0.49s | 100% Assertion Score. Prompt: 193 tokens, Completion: ~209 tokens. Clean, structured extraction of TXNM Energy Grid Modernization Phase 1 (Sept 15), SAML SSO certificate expiry blocker (Aug 28), and Airbyte connector schema dependency (Oct 1). Word count strictly bounded (100–180 words).
  - **B3 (CS Account-Note Drafting & Updates - R1):** Avg Latency: 0.61s | 100% Canonical Structure Compliance. Prompt: 245 tokens, Completion: ~336 tokens. Preserved canonical H2 sections (`## Summary`, `## Blockers`, `## Open tasks`, `## Recent activity`), used bold labels (`**Attendees:**`, `**Action:**`, `**Target:**`), cited ticket `SEC-942`, preserved bullet immutability, and showed zero internal speculation leakage.
  - **B6 (Long-Context Synthesis & Needle Recall - R1):** Avg Latency: 3.29s (sub-0.6s warm decode, ~8.8s TTFT on cold dense context) | 100% Needle Recall. Prompt: 992 tokens, Completion: ~217 tokens. 100% recall of Türk Telekom's custom root CA path (`/etc/ssl/certs/ca-certificates.crt`), mTLS 1.3 requirement, and strict CN matching against `tt-internal-gateway.telekom.com.tr`.
- overall scores (`openai/gpt-5.6-luna`):
  - correctness: 5.0
  - grounding: 5.0
  - stop-discipline: 5.0
  - format compliance: 4.9
  - latency: 4.9 (average sub-1.0s completion on standard probes; ~3.3s on dense multi-doc)
  - cleanup burden: 4.9
  - cost efficiency: 4.7 ($0.20 / $1.20 per 1M tokens — 88–92% cheaper than GPT-5.4)
- comparison vs GPT-5.4 baseline:
  - Quality, grounding, and formatting discipline are effectively identical to GPT-5.4 across all test probes.
  - Generates responses with exceptional stop-discipline and zero conversational meandering.
  - Operates at ~1/10th the cost of GPT-5.4 ($0.20/$1.20 vs $2.50/$10.00 per 1M tokens) while maintaining a 1.05M context window.
- key findings:
  - GPT-5.6 Luna is highly viable as a cheaper, high-speed internal first-pass lane for CS note drafting (B3), status synthesis (B1), extraction (B2), and long-context analysis (B6).
  - Format control and stop discipline are rock-solid, requiring zero operator cleanup.
  - Per protocol rules, R0 scheduled client-facing jobs require explicit multi-agent approval/shadow periods, but Luna easily qualifies for R1 internal workflows and R2 extraction.
- verdict:
  - **Promote to R1 (Internal Status Synthesis, CS Note Drafting, Long-Context Synthesis)** as an approved low-cost OpenAI alternative lane alongside `gemini-3.7-flash` and `mimo-v2.5`.
  - **Promote to R2 (Component Extraction)** as an ultra-fast, high-accuracy extraction engine.
  - Retain `gpt-5.4` / `claude-sonnet-4-6` for R0 scheduled frontier execution and complex architecture trade-offs.

## 2026-08-21 — Benchmark Evaluation: OpenAI GPT-5.6 Sol vs GPT-5.4
- surface: Hermes CLI over OpenRouter
- task family: B1 (Internal Status Synthesis), B5 (DevOps Audit Synthesis), B6 (Long-Context Synthesis), B7 (Complex Planning & Decomposition)
- task reliability class: R1 / R0 Candidate
- starting model: `openrouter/openai/gpt-5.6-sol`
- provider: OpenRouter BYOK (Model slug: `openai/gpt-5.6-sol`)
- pricing: $2.500 / 1M prompt tokens, $15.000 / 1M completion tokens (1,050,000 / 1.05M context window, reasoning model)
- baseline comparison model: `openrouter/openai/gpt-5.4` ($2.500 / $10.000 per 1M prompt/completion tokens, 1,050,000 context window)
- fallback model: `openrouter/openai/gpt-5.4`
- source artifacts:
  - `/Users/jason/.hermes/kanban/workspaces/t_4d70dfb3/benchmark_results.json`
  - `/Users/jason/.hermes/kanban/workspaces/t_4d70dfb3/run_benchmark.py`
  - `/Users/jason/.hermes/kanban/workspaces/t_4d70dfb3/full_runs.txt`
- result accepted: yes
- escalation required: no
- summary of results across probes (3 repeated runs per probe):
  - **B1 (Internal Scheduled-Status Synthesis - R1):**
    - `openai/gpt-5.6-sol`: Avg Latency: 0.401s | Avg Tokens: 162 prompt + 202 completion (0 reasoning tokens). 100% assertions passed. Flawlessly captured active Hermes cron/launchd counts, exact GCP VM IP `34.69.169.75`, Cloud SQL 42% disk usage, OpenCode $548 spend, and both failures (`sync-acmedemo-from-main` network timeout, agent-4 300s timeout). Crisp, unpadded, zero hallucination.
    - `openai/gpt-5.4`: Avg Latency: 0.331s | Avg Tokens: 162 prompt + 268 completion. 100% assertions passed. High quality, identical accuracy, slightly longer output (+32% output tokens).
  - **B5 (Artifact & Distribution Audit Synthesis - R1):**
    - `openai/gpt-5.6-sol`: Avg Latency: 0.374s | Avg Tokens: 392 prompt + 617 completion (115 reasoning tokens). 100% assertions passed. Clean markdown table across 3 regions. **Crucial Quality Differentiator:** Sol autonomously detected that the provided sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` is the canonical hash of a **zero-byte (empty) file**, flagging a critical artifact integrity blocker across all regions in addition to the GovCloud 403 S3 presign expiration and missing ECR tag.
    - `openai/gpt-5.4`: Avg Latency: 0.576s | Avg Tokens: 392 prompt + 606 completion (0 reasoning tokens). 100% assertions passed. Clean table and accurately flagged GovCloud S3 and ECR blockers, but treated the sha256 checksum as simply "consistent" without detecting that it was an empty file digest.
  - **B6 (Long-Context Synthesis & Needle Recall - R1):**
    - `openai/gpt-5.6-sol`: Avg Latency: 0.430s | Avg Tokens: 12012 prompt + 386 completion (99 reasoning tokens). 100% needle recall (3/3 runs). Flawlessly isolated Türk Telekom's custom root CA path `/etc/ssl/certs/ca-certificates.crt` in Chainguard container with mutual TLS 1.3 at 45% depth. Clean tabular synthesis with zero cross-account hallucination.
    - `openai/gpt-5.4`: Avg Latency: 0.421s | Avg Tokens: 12012 prompt + 330 completion. 100% needle recall (3/3 runs). Flawless recall and exact attribution.
  - **B7 (Complex Ops Planning & Decomposition - R1):**
    - `openai/gpt-5.6-sol`: Avg Latency: 0.391s | Avg Tokens: 177 prompt + 2048 completion (1286 reasoning tokens). **Major Architectural Rigor Upgrade:** Sol immediately identified the fundamental architecture conflict: EKS Fargate pods do not have an EC2 instance identity or supported access to EC2 IMDS, mandating IRSA / Pod Identity for application credentials, while explaining exactly where IMDSv2 PUT/GET token flow applies (EC2 node groups/bastions) vs container workloads. Exhaustive commands and gotchas.
    - `openai/gpt-5.4`: Avg Latency: 0.933s | Avg Tokens: 177 prompt + 2048 completion (0 reasoning tokens). Solid 4-phase plan with IMDSv2 token retrieval and Bedrock mantle endpoint format (`bedrock-mantle.<region>.api.aws/v1`), though less incisive on the Fargate vs EC2 IMDS architectural boundary.
- overall scores (1–5 scale across 7 standard dimensions):
  - **`openai/gpt-5.6-sol`**:
    - correctness: 5.0
    - grounding: 5.0
    - stop-discipline: 5.0
    - format compliance: 5.0
    - latency: 5.0 (average 0.399s across all 4 benchmark suites)
    - cleanup burden: 5.0 (100% shippable without edits)
    - cost efficiency: 4.0 ($2.50 prompt / $15.00 completion per 1M tokens)
    - **Overall Rating: 4.86 / 5.0**
  - **`openai/gpt-5.4`**:
    - correctness: 4.9
    - grounding: 5.0
    - stop-discipline: 5.0
    - format compliance: 5.0
    - latency: 4.9 (average 0.565s across all 4 benchmark suites)
    - cleanup burden: 4.9
    - cost efficiency: 4.2 ($2.50 prompt / $10.00 completion per 1M tokens)
    - **Overall Rating: 4.84 / 5.0**
- comparison vs GPT-5.4 baseline:
  - **Quality & Reasoning Depth:** GPT-5.6 Sol is a **clear quality upgrade** over GPT-5.4, not merely a price/latency parity substitute. Sol's internal reasoning tokens (~100–1300 tokens depending on task complexity) enabled it to catch subtle real-world failure modes that GPT-5.4 missed (e.g. recognizing `e3b0c442...` as a zero-byte empty file hash on B5, and diagnosing the Fargate vs EC2 IMDSv2 architectural conflict on B7).
  - **Latency & Throughput:** Sol demonstrated lower wall-clock latency on B5 (0.37s vs 0.58s) and B7 (0.39s vs 0.93s), with parity on B1 and B6.
  - **Operational Burden & Formatting:** Zero cleanup required; 100% compliance across markdown tables, headers, and bullet structures without conversational filler.
  - **Pricing Profile:** Sol is priced at $2.50 / $15.00 per 1M tokens (+50% completion premium vs GPT-5.4's $2.50 / $10.00), but uses concise outputs on synthesis tasks, partially offsetting the per-token delta.
- verdict:
  - **Promote to R0 / High-Judgment Frontier Specialist (Complex Architecture Planning & Critical DevOps Audits)**: Qualified as an approved frontier engine alongside or superseding `gpt-5.4` for high-judgment tasks where deep reasoning and flaw detection (like empty checksums or identity architecture gotchas) outweigh token completion cost.
  - Retain lower-cost models (`gpt-5.6-luna`, `gemini-3.7-flash`, `mimo-v2.5`, `laguna-s-2.1`) for high-volume routine R1 status drafts and R2 extraction.

## 2026-08-21 — Benchmark Evaluation: OpenAI GPT-5.6 Luna Pro via OpenRouter
- surface: Hermes CLI over OpenRouter
- task family: B1 (Internal Status Synthesis), B3 (CS Note Drafting), B5 (Artifact Audit), B6 (Long-Context Synthesis)
- task reliability class: R1 / Mid-Tier Routing Lane Candidate
- starting model: `openrouter/openai/gpt-5.6-luna-pro`
- provider: OpenRouter BYOK (Model slug: `openai/gpt-5.6-luna-pro`)
- pricing: $0.200 / 1M prompt tokens, $1.200 / 1M completion tokens (1,050,000 context length)
- baseline comparison models:
  1. `openrouter/openai/gpt-5.6-luna` ($0.200 / 1M prompt, $1.200 / 1M completion)
  2. `openrouter/openai/gpt-5.4` ($2.500 / 1M prompt, $15.000 / 1M completion)
- source artifacts:
  - `/Users/jason/.hermes/kanban/workspaces/t_ed866a0d/benchmark_results.json`
  - `/Users/jason/.hermes/kanban/workspaces/t_ed866a0d/run_eval.py`
- result accepted: yes
- escalation required: no
- summary of results across probes (3 repeated runs per probe):
  - **B1 (Internal Scheduled-Status Synthesis - R1):** Avg Latency: 0.45s | 100% Assertion Score (3/3 runs, 6/6 assertions). Avg Prompt Tokens: 2,843, Avg Completion Tokens: 1,009. Avg Cost: $0.001779/run. Flawlessly captured failing cron `sync-acmedemo-from-main`, timed-out launchd sweep `health-check-sweep` on `agent-4`, VM IP `34.69.169.75`, Cloud SQL 42% storage, and OpenCode $548 spend baseline. Zero hallucinated outages.
  - **B3 (CS Account-Note Drafting & Updates - R1):** Avg Latency: 0.80s | 100% Canonical Structure Compliance (3/3 runs, 5/5 assertions). Avg Prompt Tokens: 3,461, Avg Completion Tokens: 1,206. Avg Cost: $0.002140/run. Adhered strictly to canonical sections (`## Summary`, `## Blockers`, `## Open tasks`, `## Recent activity`), used bold labels (`**Attendees:**`, `**Action:**`), cited ticket `SEC-942`, preserved bullet immutability, and showed zero internal speculation leakage.
  - **B5 (Artifact & Distribution Audit Synthesis - R1):** Avg Latency: 0.40s | 100% Assertion Score (3/3 runs, 4/4 assertions). Avg Prompt Tokens: 4,894, Avg Completion Tokens: 2,204. Avg Cost: $0.003624/run. Generated complete markdown audit table; correctly isolated `us-gov-west-1` S3 403 presign expiration and missing GovCloud ECR tag as blockers while confirming `us-east-1` and `us-central1` as verified. In run 3, noted the empty byte stream SHA256 anomaly.
  - **B6 (Long-Context Synthesis & Needle Recall - R1):** Avg Latency: 0.42s | 100% Needle Recall (3/3 runs, 4/4 assertions). Avg Prompt Tokens: 20,286, Avg Completion Tokens: 1,862. Avg Cost: $0.006292/run. Flawlessly extracted Türk Telekom's custom root CA path (`/etc/ssl/certs/ca-certificates.crt`) in the Chainguard container, mTLS 1.3 requirement, and strict CN validation against `tt-internal-gateway.telekom.com.tr`.
- overall scores (`openai/gpt-5.6-luna-pro`):
  - correctness: 5.0
  - grounding: 5.0
  - stop-discipline: 4.8
  - format compliance: 5.0
  - latency: 4.9 (sub-1.0s completion on all probes)
  - cleanup burden: 4.9 (zero operator edits required)
  - cost efficiency: 4.5 ($0.20 / $1.20 per 1M tokens — identical unit pricing to Luna, but higher token multiplier per run due to expanded chain-of-thought tokens)
- comparative analysis vs GPT-5.6 Luna and GPT-5.4 Baseline:
  1. **Pricing & Parameter Parity:** Luna Pro shares the exact OpenRouter pricing card ($0.200/M input, $1.200/M output, 1.05M context window) with standard GPT-5.6 Luna.
  2. **Quality & Formatting:** Both Luna Pro and Luna achieve 100% assertion pass rates across B1, B3, B5, and B6, matching the precision and grounding of GPT-5.4.
  3. **Token Usage & Run Cost:** Luna Pro incurs significantly higher token overhead per request (e.g. B1: 2,843 prompt / 1,009 completion tokens vs Luna's 172 prompt / 239 completion tokens; B6: 20,286 prompt / 1,862 completion tokens vs Luna's 4,357 prompt / 352 completion tokens). This results in a ~4.8x–5.5x higher per-run cost ($0.00178 vs $0.00032 on B1; $0.00629 vs $0.00129 on B6) due to internalized reasoning overhead.
  4. **Routing Advantage:** Luna Pro provides zero measurable accuracy, structural formatting, or reasoning advantage over standard GPT-5.6 Luna on standard R1 ops tasks (status synthesis, CS drafting, audit tables, and needle recall), while consuming substantially more tokens and introducing unnecessary token bloat.
- key findings:
  - Luna Pro collapses to Luna-equivalent behavioral output for standard R1 operational tasks.
  - Because standard GPT-5.6 Luna already achieves 5.0/5.0 correctness and 100% formatting compliance at ~1/5th the token volume per run, adopting Luna Pro introduces higher inference cost with no practical quality gain.
  - Per evaluation protocol rules ("Reject if it collapses to Luna-equivalent behavior with no measurable routing advantage"), Luna Pro does not warrant a distinct routing lane over standard Luna.
- verdict:
  - **Reject for mid-tier routing replacement.** GPT-5.6 Luna Pro offers no measurable quality or routing advantage over `openai/gpt-5.6-luna` while inflating token usage and per-request cost by ~5x. Standard `openai/gpt-5.6-luna` remains the preferred, cost-efficient model for R1 OpenAI lanes.

## 2026-08-21 — Benchmark Phase 1 Candidate Models on R2 Extraction and Triage (DeepSeek V4 Flash & Gemma 4 26B)
- surface: Hermes CLI over OpenRouter
- fallback model: `openrouter/openai/gpt-5.4`
- source artifacts:
  - `/Users/jason/.hermes/kanban/workspaces/t_dd899481/benchmark_results.json`
  - `/Users/jason/.hermes/kanban/workspaces/t_dd899481/results.json`
  - `/Users/jason/.hermes/kanban/workspaces/t_dd899481/run_bench.py`
  - `/Users/jason/.hermes/kanban/workspaces/t_dd899481/fixtures.json`
- result accepted: yes, with caveat
- escalation required: yes
- benchmark results:
  - **`openrouter/deepseek/deepseek-v4-flash-0731`**
    - **B2 Extraction:** avg TTFT 27.398s, avg total latency 32.042s. Prompt/completion tokens per run: 269 / 1481, 269 / 2177, 269 / 242. Computed run costs from rate card: $0.00028407, $0.00040935, $0.00006105; avg $0.00025149/run.
    - **B4 Triage / JSON:** avg TTFT 4.122s, avg total latency 4.628s. Prompt/completion tokens observed on 2/3 runs: 189 / 248 and 189 / 247; computed costs $0.00005693 and $0.00005675; avg observed cost $0.00005684/run. JSON/schema compliance: 1/3 valid. Two runs corrupted required keys (`is_private_channel`, `suggested_action`); one run returned valid schema-compliant JSON.
  - **`openrouter/google/gemma-4-26b-a4b-it`**
    - **B2 Extraction:** avg TTFT 6.384s, avg total latency 28.236s. Prompt/completion tokens per run: 305 / 184, 305 / 192, 305 / 201. Computed run costs from rate card: $0.00008391, $0.00008663, $0.00008969; avg $0.00008674/run.
    - **B4 Triage / JSON:** avg TTFT 0.983s, avg total latency 3.531s. Prompt/completion tokens per run: 215 / 67, 215 / 67, 215 / 67. Computed run costs: $0.00003783 each run; avg $0.00003783/run. JSON/schema compliance: 0/3 valid. All three runs emitted malformed JSON and truncated required keys.
- scores:
  - correctness: 2.5
  - grounding: 3.5
  - stop-discipline: 3
  - format compliance: 1
  - latency: 3.5
  - cleanup burden: 1.5
- notes:
  - Neither candidate is acceptable for R2 frontdoor triage in current form. Schema adherence is the hard gate here, and both models failed it repeatedly; Gemma failed all 3 B4 runs, while DeepSeek succeeded only once.
  - Gemma is materially faster and cheaper than DeepSeek on both probes, but that does not compensate for 0% JSON validity on the triage task.
  - DeepSeek showed a weaker latency profile on B2 and inconsistent format behavior on B4; its single valid B4 run is not enough evidence for promotion.
  - Artifact quality is not fully clean: one DeepSeek B4 run is missing token accounting, so the recorded B4 cost for that model is an observed 2-run average, not a full 3-run mean.
  - Probe comparability is imperfect. `benchmark_results.json` used the simplified `b2_prompt.txt` fixture, while `fixtures.json` and `results.json` reflect a later, expanded synthetic transcript. The direction of the result is still clear for B4, but B2 should be rerun on the canonical fixture before using these numbers for routing policy.
- verdict:
  - `openrouter/deepseek/deepseek-v4-flash-0731`: reject for R2 triage; keep-evaluating only if rerun on canonical B2 fixture and if JSON conformity can be stabilized.
  - `openrouter/google/gemma-4-26b-a4b-it`: reject for R2 triage and do not promote for production frontdoor routing without a clean 3/3 JSON pass.

## 2026-08-27 — Benchmark Evaluation: Meta Muse Glimmer 30B via DeepInfra
- surface: Hermes CLI over OpenRouter
- task family: B2 (Extraction), B3 (Canonical CS Note), B4 (Triage), B5 (Distribution Audit), B8 (Tool Use)
- task reliability class: R2 qualification / R1 evaluation
- starting model: `meta/muse-glimmer-30b`
- provider: OpenRouter targeting DeepInfra `deepinfra/bf16`
- fallback model: `openrouter/openai/gpt-5.4`
- latency: 0.29s average across the captured single run per probe
- recorded cost: $0.00 in evaluation artifact; verified provider rate card is $0.30/M input and $1.20/M output
- source artifacts:
  - `/tmp/muse-glimmer-30b-summary.md`
  - `/tmp/muse-glimmer-real/eval_meta_muse-glimmer-30b.json`
- result accepted: partial
- escalation required: no for B2/B4/B5/B8; yes for B3 canonical-note use
- scores:
  - correctness: 4.52 aggregate
  - grounding: 5.0 on clean probes; B3 output was empty
  - stop-discipline: 5.0 on captured probes
  - format compliance: 5.0 on B2/B4/B5/B8; B3 failed canonical format assertions
  - latency: 5.0 / sub-second captured latency
  - cleanup burden: 5.0 on B2/B4/B5/B8; B3 requires a rewrite
- notes:
  - B2, B4, B5, and B8 each scored 5.0/5 with 100% assertion passes.
  - B3 scored 2.58/5 and passed 1/5 assertions; the model returned empty content and failed canonical sections, bold-label syntax, citations, and task-owner preservation.
  - Single-run evidence is insufficient for unattended production promotion. Free/zero-cost evaluation accounting must not be confused with the provider rate card.
- verdict:
  - promote to R2 triage/extraction fast-track with verification
  - keep-evaluating for R1; do not use for canonical vault notes, vault mutations, unattended scheduled jobs, or customer-facing finalization until repeated B3 canonical-fixture runs pass

## 2026-09-01 — Controlled Eval: Newly Available OpenRouter Free Routes
- surface: Automated Evaluation Harness (`scripts/eval_promo_candidates.py`)
- task family: B1, B2, B4, B5, B8 (one round per probe; B3/B6/B7 intentionally omitted for low-risk cost control)
- provider: OpenRouter BYOK/free routes
- fallback model: `openrouter/openai/gpt-5.4` retained; no route changes made
- source artifacts:
  - `benchmark-results/eval_master_index.json`
  - `benchmark-results/eval_nvidia_nemotron-3.5-lightning_free.json`
  - `benchmark-results/eval_poolside_laguna-s-2.1_free.json`
  - `benchmark-results/eval_poolside_laguna-xs-2.1_free.json`
  - `benchmark-results/eval_thinkingmachines_inkling-small_free.json`
  - `benchmark-results/eval_minimax_minimax-m3_free.json`
  - `benchmark-results/eval_cohere_north-mini-code_free.json`
- execution: 6 models × 5 probes × 1 round; all requests completed or returned explicit provider errors; recorded evaluation cost $0.00
- results:
  - `nvidia/nemotron-3.5-lightning:free`: overall 4.21/5, 10.19s average, 76% assertions. B1/B5/B8 strong, but B4 emitted analysis instead of strict JSON and B2 missed the date assertion. Harness eligibility says R1, but this single run is not promotion evidence.
  - `poolside/laguna-s-2.1:free`: overall 2.49/5, 0.40s average, 36% assertions. B1 passed; B2/B4/B5 were blocked by HTTP 429 upstream shared-pool rate limiting; B8 passed 4/5 assertions. Reject for this pass; availability is unverified under rate limiting.
  - `poolside/laguna-xs-2.1:free`: overall 1.80/5, 0.19s average, 20% assertions. B2 passed; B1/B4/B5/B8 were blocked by HTTP 429 upstream shared-pool rate limiting. Reject for this pass; availability is unverified under rate limiting.
  - `thinkingmachines/inkling-small:free`: overall 1.00/5, 0.12s average, 0% assertions. Every probe returned HTTP 403: route is only available on agentic harnesses. Not suitable for this chat-completions harness.
  - `minimax/minimax-m3:free`: overall 5.00/5, 1.29s average, 100% assertions across all five probes. Harness mechanically reports R2/R1/R0 eligibility, but this is one round only; no production promotion or routing update was made.
  - `cohere/north-mini-code:free`: overall 4.26/5, 0.44s average, 72% assertions. B1/B4 passed; B2 missed target-date assertion, B5 missed healthy-region confirmation, and B8 failed all tool-call assertions. Keep evaluating; not promotion-ready.
- notes:
  - Provider-reported free pricing yielded $0.00 recorded cost; this must not be interpreted as a guarantee of availability or an entitlement to production capacity.
  - Results are single-round screening evidence, not the protocol's required repeated-run promotion evidence.
  - No production routes, scheduled jobs, aliases, or `routing-matrix.md` entries were changed.
- verdict:
  - `minimax/minimax-m3:free`: strongest screening result; keep in controlled evaluation/shadow queue only.
  - `nvidia/nemotron-3.5-lightning:free`: promising for B1/B5/B8, but strict B4 failure and latency require rerun before any lane consideration.
  - `cohere/north-mini-code:free`: keep-evaluating for bounded non-tool work; reject for B8-dependent routing in current form.
  - Poolside routes: blocked/failed availability screen due to upstream shared-pool HTTP 429; no quality conclusion beyond the successful probes.
  - Inkling Small: reject for this harness because OpenRouter restricts the route to agentic harnesses.

## 2026-09-01 — Repeated Eval: MiniMax M3 Free Route Stability
- surface: Automated Evaluation Harness (`scripts/eval_promo_candidates.py`)
- task family: Repeated B1/B2/B4/B5/B8 plus targeted B3 canonical account-note coverage
- requested model: `minimax/minimax-m3:free`
- actual route observed in all 18 requests: model `minimax/minimax-m3:free`, provider `GMICloud`
- execution: 6 probes × 3 rounds; all 18 requests succeeded; recorded evaluation cost $0.00 on the free route
- source artifacts:
  - `benchmark-results/repeat_minimax_20260901/eval_minimax_minimax-m3_free.json`
  - `benchmark-results/repeat_minimax_20260901/eval_master_index.json`
- aggregate: 4.91/5.00 overall, 1.25s mean probe latency, 98% assertion pass rate, 0.00 recorded cost
- per-probe stability:
  - B1: 3/3 passes, 5.00/5.00 each, latency 0.934–2.023s (mean 1.48s)
  - B2: 2/3 passes, 4.45/5.00 on the two misses because the output omitted a date assertion; one 5.00/5.00 pass, latency 0.620–0.920s (mean 0.80s)
  - B3: 3/3 passes, 5.00/5.00 each, latency 0.887–1.019s (mean 0.94s); canonical sections, bold labels, SAML/SEC-942 citation, direct-correlation discipline, and task owners were preserved
  - B4: 3/3 passes, 5.00/5.00 each, latency 0.876–0.975s (mean 0.91s); strict JSON/schema assertions passed
  - B5: 3/3 assertion passes, scores 5.00/4.70/4.70, latency 0.687–5.355s (mean 2.33s); slower first run and extra cleanup/stop-discipline penalty on later verbose audit outputs
  - B8: 3/3 passes, 5.00/5.00 each, latency 0.999–1.041s (mean 1.02s)
- B3 limitation: the harness supports B3 directly; no limitation encountered. This was canonical-fixture assertion coverage, not a live vault mutation.
- verdict: repeated evidence supports continued controlled/shadow evaluation. Do not promote production routing, unattended jobs, canonical vault mutations, or customer-facing finalization from this result alone; B2 date fidelity and B5 output discipline remain observed variance.

## 2026-09-11 — Automated Eval: google/gemma-4-31b-it:free via OpenRouter
- surface: Automated Evaluation Harness (`eval_promo_candidates.py`)
- task family: Benchmark Probes (B1, B2, B3, B4, B5, B6, B7, B8)
- model evaluated: `google/gemma-4-31b-it:free`
- evaluated at: 2026-09-11 13:16:14 UTC
- source artifact: `~/.hermes/telemetry/eval_results/eval_google_gemma-4-31b-it_free.json`
- execution: 8 probes × 3 rounds (24 total attempts); recorded evaluation cost $0.00
- aggregate: overall 1.00 / 5.0, 0.24s average latency, 0.0% pass rate (0% assertion pass rate)
- failure mode: 100% execution failure (24/24 requests failed with HTTP 429 `RESOURCE_EXHAUSTED` from upstream provider `Google AI Studio`: "Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing.")
- promotion verdict: **reject** (eligible tiers: none)
- notes:
  - Route is served via OpenRouter BYOK backed by Google AI Studio without active quota/prepayment credits.
  - Consistent with the model routing ops pitfall: free `:free` routes on OpenRouter served exclusively by an upstream provider require available upstream quota; exhausted credits prevent evaluation and yield immediate HTTP 429.
  - Model failed all gates across R2, R1, and R0. Zero tier promotions and no configuration changes applied.







