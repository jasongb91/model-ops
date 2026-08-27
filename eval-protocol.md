---
date: 2026-08-21
type: evaluation-protocol
status: active
priority: ops-cs
---

# Standard Model Ops Evaluation Protocol & Benchmark Suite

Purpose: Standardized evaluation protocol, scoring methodology, and test dataset for evaluating external LLMs via OpenRouter for CS and Model Ops workflows.

---

## 1. Evaluation Criteria & Scoring Framework

Every candidate model evaluated via OpenRouter must be scored across 7 standard dimensions (1–5 scale) and 2 gating pass/fail criteria:

### Quantitative Scoring Dimensions (1–5 scale)
1. **Correctness (1–5):** Factual accuracy, absence of hallucinations, valid logic, correct analytical verdicts.
2. **Grounding & Evidence Use (1–5):** Explicit citation of input artifacts, logs, telemetry, or documents. 0 tolerance for fabricated entity names, IPs, hostnames, or metrics.
3. **Stop-Discipline (1–5):** Clean termination without conversational meandering, generic filler padding, or unrequested self-dialogue / chain-of-thought leaks in user-facing surfaces.
4. **Format Compliance (1–5):** Strict adherence to required output formats (JSON schemas, Markdown headers, table structures, bullet immutability, bold label conventions).
5. **Latency (1–5):** Time-to-first-token (TTFT), tokens-per-second decode, and total wall-clock duration against task-family latency budgets.
6. **Operator Cleanup Burden (1–5):** Degree of manual editing required before an output can be accepted or dispatched (5 = zero edit required, 1 = total rewrite).
7. **Recorded Cost / Token Efficiency (1–5):** Cost per thousand/million tokens on OpenRouter, token multiplier overhead, and cache hit efficiency.

### Pass/Fail Gating Criteria
- **Escalation Required:** Did the model fail to meet the task's reliability class requirements, forcing failover to a frontier fallback (`openai/gpt-5.4` or `anthropic/claude-sonnet-4-6`)?
- **Shippable Without Rewrite:** Could the raw output be delivered directly to the target system or user without human intervention?

---

## 2. Task Families & Benchmark Suite (B1–B8)

| Benchmark ID | Task Family | Reliability Class | Latency Budget | Target Output Format | Key Evaluation Focus |
|---|---|:---:|:---:|---|---|
| **B1** | Internal Scheduled-Status Synthesis | R1 | < 20s | Structured Markdown / BLUF | Multi-system telemetry distillation, crisp bulleting, no hallucinated outages. |
| **B2** | Morning Brief Component Extraction | R1/R2 | < 10s | Key-value / bullet points | Rapid account fact extraction, high throughput, low token cost. |
| **B3** | CS Account-Note Drafting & Updates | R1 | < 30s | Vault canonical Markdown | Direct-Correlation compliance, bullet immutability, no internal commentary leaks. |
| **B4** | Frontdoor / Slack Triage & Classification | R2 | < 8s | Strict JSON Schema | Accurate routing, strict channel exclusion & privacy policy enforcement. |
| **B5** | Artifact & Distribution Audit Synthesis | R1 | < 25s | Markdown Tables & Remediation | Tabular telemetry analysis, blocker highlighting, zero missed anomalies. |
| **B6** | Long-Context Synthesis & Needle Recall | R1 | < 45s | Executive Summary / Report | >30k–128k token context retention, 100% needle recall, cost scaling. |
| **B7** | Complex Ops Planning & Decomposition | R1 | < 40s | Phased Execution Plan | Dependency mapping, gotcha awareness, validation command precision. |
| **B8** | Agent Tool Use & Structured Execution | R1 | < 25s | Tool Call / JSON Arguments | Function calling schema validity, parameter type compliance, recovery from tool errors. |

---

## 3. Standardized Test Dataset & Probes

The standardized test dataset comprises 8 bounded test probes mapped directly to the benchmark suite:

### Probe B1: Multi-System Ops Telemetry Digest
- **Input Context:** Raw logs containing Hermes cron status (2 jobs active, 1 failure), launchd sweeps (7 agents, 1 timed out), GCP VM status (`acmedemo` healthy @ 34.69.169.75, Cloud SQL 42% storage), and OpenCode 14-day spend metrics ($548 baseline).
- **Task Prompt:** *"Generate a concise internal ops status brief. Summarize active systems, flag operational failures, and list immediate remediation actions in bullet form."*
- **Ground Truth Assertions:**
  1. Identifies the exact failing Hermes cron job and timed-out launchd agent.
  2. Quotes the correct GCP VM IP and Cloud SQL storage percentage.
  3. Proposes remediation without inventing unrelated system errors.

### Probe B2: Account Activity Extraction (TXNM Energy Log)
- **Input Context:** Raw customer interaction transcript from TXNM Energy (3 meeting notes, 2 email threads discussing Grid Modernization rollout, 1 blocker regarding SAML SSO cert expiry).
- **Task Prompt:** *"Extract key customer movement, new blockers, and upcoming milestones from the TXNM Energy interaction transcript. Output 3-5 high-signal bullets ready for morning ops briefing."*
- **Ground Truth Assertions:**
  1. Highlights the SAML SSO certificate expiry blocker explicitly.
  2. Extracts exact target rollout dates.
  3. Output length bounded between 100–180 words.

### Probe B3: Customer Account Note Update (Vault Canonical Format)
- **Input Context:** Direct customer meeting notes with TXNM Energy stakeholders discussing milestone completion and architecture signoff.
- **Task Prompt:** *"Draft the weekly update entry for `customer-accounts/txnm-energy.md`. Strictly adhere to canonical sections (## Onboarding, ## Blockers, ## Open tasks, ## Recent activity), maintain bullet immutability, and respect Direct-Correlation rules."*
- **Ground Truth Assertions:**
  1. Preserves existing bullet text unchanged; only appends new bullets or marks completed with resolution evidence.
  2. Does not leak internal-only commentary or threat-intel speculation into the customer note.
  3. Employs bold-label syntax (`**Attendees:**`, `**Action:**`).

### Probe B4: Inbound Slack Intake & Triage Classification
- **Input Context:** Inbound message: *"Hey team, we're seeing intermittent 502 errors on the Acmedemo REST API port 8082 during peak traffic. Can someone check the crogld service logs?"* Inbound channel: `#ops-intake` (public).
- **Task Prompt:** *"Classify the inbound message. Return JSON with fields `route` ('cs-ops' | 'solutions-architect' | 'build' | 'direct-reply'), `urgency` ('P1' | 'P2' | 'P3'), `is_private_channel` (boolean), `privacy_violation` (boolean), and `suggested_action`."*
- **Ground Truth Assertions:**
  1. Valid JSON matching the schema with 0 markdown backticks or commentary if specified.
  2. `route` equals `cs-ops` or `solutions-architect`.
  3. `urgency` classified as `P2` or `P1`.
  4. Correct privacy assessment (`privacy_violation: false`).

### Probe B5: Release Artifact & ECR/S3 Distribution Audit
- **Input Context:** Multi-region build telemetry table for release `v2.4.0-rc3` across AWS us-east-1, us-gov-west-1, and GCP us-central1. Contains sha256 checksums, 1 failed S3 presign URL, and 1 missing container tag in GovCloud ECR.
- **Task Prompt:** *"Audit the distribution matrix for release v2.4.0-rc3. Output a markdown status table and explicitly list blockers preventing release promotion."*
- **Ground Truth Assertions:**
  1. Flags the failed S3 presign URL and GovCloud ECR tag discrepancy as blocking issues.
  2. Generates a clean markdown table with regional availability status.
  3. Correctly identifies unaffected regions as green/verified.

### Probe B6: Long-Context Needle-in-a-Haystack & Multi-Doc Synthesis
- **Input Context:** Synthetic/aggregated ~30,000–60,000 token vault corpus consisting of 25 customer notes, architecture docs, and meeting logs. A unique security requirement ("*Türk Telekom requires mutual TLS 1.3 with custom root CA cert in Chainguard container /etc/ssl/certs/ca-certificates.crt*") is placed at the 45% depth mark.
- **Task Prompt:** *"Synthesize enterprise customer trust-store requirements across all customer accounts. Identify any custom root CA certificate paths required for air-gapped or self-hosted deployments."*
- **Ground Truth Assertions:**
  1. 100% recall of the exact container path `/etc/ssl/certs/ca-certificates.crt`.
  2. Correct attribution to Türk Telekom without hallucinating requirements for other accounts.

### Probe B7: Architecture Planning & Dependency Decomposition
- **Input Context:** Requirement spec to migrate an internal agent backend to GovCloud EKS Fargate using IMDSv2, AWS Bedrock mantle endpoints, and custom IAM role bindings.
- **Task Prompt:** *"Create a phased technical execution plan with dependency ordering, potential failure gotchas (IMDS hostname resolution, Bedrock tool schema formats, Fargate logging), and exact verification commands."*
- **Ground Truth Assertions:**
  1. Explicitly identifies the Bedrock mantle endpoint format (`bedrock-mantle.<region>.api.aws/v1`) vs standard runtime.
  2. Includes IMDSv2 token-fetching steps and exact `aws` CLI verification commands.
  3. Structures the output into clear phases (Preflight, Implementation, Verification, Rollback).

### Probe B8: Agent Tool-Use & Function Schema Compliance
- **Input Context:** Tool definitions for `mcp__crogld__crowdstrike_falcon_query` and `mcp__crogld__create_investigation`. User prompt: *"Run a query on crowdstrike falcon for SHA256 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' and open an investigation ticket."*
- **Task Prompt:** *"Execute the appropriate tool calls to query the hash and create the investigation."*
- **Ground Truth Assertions:**
  1. Produces valid OpenAI-format tool call objects with stringified JSON arguments.
  2. Emits correct function names without illegal characters.
  3. No hallucinated parameter names.

---

## 4. OpenRouter Execution Protocol

When testing a candidate model via OpenRouter:
1. **Model ID Resolution:** Verify the exact OpenRouter model slug (e.g., `openrouter/nvidia/nemotron-3-super-120b`, `openrouter/xiaomi/mimo-v2.5`, `openrouter/qwen/qwen3.7-flash`).
2. **Parameters Baseline:** Set `temperature: 0.2`, `top_p: 0.95`, `max_tokens: 4096` (or model default), `data_collection: deny`.
3. **Execution Rounds:** Execute each probe 3 times to measure variance across latency, stop-discipline, and formatting consistency.
4. **Telemetry Capture:** Record exact time-to-first-token, completion latency, prompt tokens, completion tokens, and dollar cost based on OpenRouter published rates.
5. **Score Logging:** Document results in `experiment-log.md` using the standard experiment template.

---

## 5. Promotion & Routing Matrix Decision Rules

A candidate model is eligible for promotion into `routing-matrix.md` under the following conditions:

- **Promotion to R2 (Low-Risk / Triage / Extraction):**
  - **Fast-Track Score Threshold:** Average score $\ge 4.8$ across B2 and B4.
  - 0 format compliance failures (100% valid JSON / clean bullets).
  - Material latency (<10s) or cost advantage (>50% savings vs current R2 lane).
  - Fast-tracks immediately to chat aliases, frontdoor triage, and extraction defaults.

- **Promotion to R1 (Internal Ops / Drafting / Synthesis):**
  - **Fast-Track Score Threshold:** Average score $\ge 4.8$ across B1, B3, B5, B6, B7, B8.
  - Zero critical hallucinations (100% precision on entities, IPs, paths).
  - Stop-discipline score $\ge 4.5$.
  - Stable performance across 3 repeated runs per probe.
  - Promotes directly to internal drafting, synthesis, and OpenCode worker defaults.

- **Promotion to R0 (Scheduled / Client-Facing / Frontier):**
  - **Promotion Score Threshold:** Average score $\ge 4.9$ across all operational probes.
  - Zero cleanup burden (Operator cleanup score = 5.0, 100% shippable without human intervention).
  - **Mandatory 3-Day Shadow Window:** 3 consecutive execution cycles in shadow mode diffed against active baseline with zero regressions.
  - **Frontier Fallback Requirement:** Hardcoded escalation ladders to `openai/gpt-5.4`, `openai/gpt-5.6-sol`, or `anthropic/claude-sonnet-4-6` retained. Rate-limited `:free` endpoints restricted to shadow evaluation.
