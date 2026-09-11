# Model Ops Routing Alignment Implementation Plan

> **For Hermes:** Execute this plan task-by-task to align delegated prompts, launchd scripts, and skill definitions with `model-ops` routing policy.

**Goal:** Eliminate legacy/hardcoded references to `openai/gpt-5.4` across Hermes cron prompts, OpenCode dispatch skills, and launchd shell/Python bridges, replacing them with evaluated cost-effective Model Ops ladders (`laguna-s-2.1`, `gpt-5.6-luna`, `nemotron-3-ultra-550b:free`, `gemini-3.7-flash`, `gpt-5.6-sol`).

**Architecture:** 
1. **Layer 1 (Hermes Cron Configuration):** Update `ops-morning-briefing` prompt in `jobs.json` to instruct OpenCode `cs-ops` delegation using the Model Ops R0 ladder (`laguna-s-2.1` / `gpt-5.6-luna` primary, `gpt-5.6-sol` / `gemini-3.7-flash` fallback).
2. **Layer 2 (Bridge Scripts):** Parameterize and update default model flags in `/Users/jason/scripts/morning-ops-hermes.sh` and `/Users/jason/vault/scripts/account-enrichment-hermes.sh`, `eod-progress-sweep.sh`, `account-decay-sweep.sh`, `watch-transcripts.sh`.
3. **Layer 3 (Skills & Dispatch Governance):** Update `vault-opencode-dispatch` skill references (`model-routing.md`, `SKILL.md`, `repo_dispatch_helper.py`) and `ops-morning-briefing` to reflect modern Model Ops defaults.

**Tech Stack:** Python, Bash, JSON, Markdown, OpenCode Dispatcher, Hermes Cron.

---

### Task 1: Update `ops-morning-briefing` Cron Prompt in `jobs.json`

**Objective:** Update the delegated `cs-ops` model ladder in the `ops-morning-briefing` cron prompt from `openai/gpt-5.4` to Model Ops verified defaults.

**Files:**
- Modify: `/Users/jason/.hermes/profiles/ops/cron/jobs.json:6`

**Step 1: Backup `jobs.json`**
```bash
cp /Users/jason/.hermes/profiles/ops/cron/jobs.json /Users/jason/.hermes/profiles/ops/cron/jobs.json.bak
```

**Step 2: Apply Patch to `jobs.json`**
Change the delegated model instruction from:
`primary openai/gpt-5.4, fallback deepinfra/deepseek-ai/DeepSeek-V3.2`
to:
`primary openrouter/openai/gpt-5.6-luna, fallback openrouter/openai/gpt-5.6-sol`

**Step 3: Verification**
Validate valid JSON syntax and check matching prompt string:
```bash
python3 -c "import json; data = json.load(open('/Users/jason/.hermes/profiles/ops/cron/jobs.json')); print('Valid JSON:', len(data['jobs']))"
```

---

### Task 2: Align `morning-ops-hermes.sh` with Model Ops Ladder

**Objective:** Update `/Users/jason/scripts/morning-ops-hermes.sh` so its Hermes CLI and OpenCode dispatch sub-passes use Model Ops evaluated models instead of hardcoded `openai/gpt-5.4`.

**Files:**
- Modify: `/Users/jason/scripts/morning-ops-hermes.sh`

**Step 1: Inspect and patch model variables**
- In `run_hermes_query` (line 108): change `-m openai/gpt-5.4` to `-m ${HERMES_SYNTH_MODEL:-openrouter/google/gemini-3.7-flash}`.
- In `run_dispatch_phase` (lines 215-216):
  - `--model ${MORNING_OPS_DISPATCH_MODEL:-openrouter/openai/gpt-5.6-luna}`
  - `--fallback-model ${MORNING_OPS_FALLBACK_MODEL:-openrouter/openai/gpt-5.6-sol}`

**Step 2: Verification**
```bash
bash -n /Users/jason/scripts/morning-ops-hermes.sh
/Users/jason/scripts/morning-ops-hermes.sh --probe
```

---

### Task 3: Align Launchd Sweeps and Vault Bridge Scripts

**Objective:** Update default fallback and escalation models across vault bridge scripts in `/Users/jason/vault/scripts/`.

**Files:**
- Modify: `/Users/jason/vault/scripts/account-enrichment-hermes.sh`
- Modify: `/Users/jason/vault/scripts/watch-transcripts.sh`
- Modify: `/Users/jason/vault/scripts/process_transcript.py`
- Modify: `/Users/jason/vault/scripts/eod-progress-sweep.sh`
- Modify: `/Users/jason/vault/scripts/account-decay-sweep.sh`
- Modify: `/Users/jason/vault/scripts/AGENTS.md`

**Step 1: Apply updates**
- `account-enrichment-hermes.sh`: update Hermes chat command to use `openrouter/xiaomi/mimo-v2.5` or `openrouter/openai/gpt-5.6-luna`.
- `watch-transcripts.sh` / `process_transcript.py`: update default escalation from `openrouter/openai/gpt-5.4` to `openrouter/minimax/minimax-m3` and `openrouter/openai/gpt-5.6-luna`.
- `eod-progress-sweep.sh` / `account-decay-sweep.sh`: update escalation default from `openrouter/openai/gpt-5.4` to `openrouter/poolside/laguna-s-2.1` and `openrouter/google/gemini-3.7-flash`.
- `AGENTS.md`: update line 9 from `openai/gpt-5.4` default to current Model Ops matrix.

**Step 2: Verification**
Verify bash script syntax for all touched shell scripts:
```bash
bash -n /Users/jason/vault/scripts/account-enrichment-hermes.sh
bash -n /Users/jason/vault/scripts/watch-transcripts.sh
bash -n /Users/jason/vault/scripts/eod-progress-sweep.sh
bash -n /Users/jason/vault/scripts/account-decay-sweep.sh
```

---

### Task 4: Update `vault-opencode-dispatch` Governance & Dispatch Helper

**Objective:** Align `vault-opencode-dispatch` skills documentation, model routing reference, and `repo_dispatch_helper.py` with Model Ops standards.

**Files:**
- Modify: `/Users/jason/.hermes/profiles/ops/skills/vault-opencode-dispatch/references/model-routing.md`
- Modify: `/Users/jason/.hermes/profiles/ops/skills/vault-opencode-dispatch/SKILL.md`
- Modify: `/Users/jason/.hermes/profiles/ops/skills/vault-opencode-dispatch/scripts/repo_dispatch_helper.py`

**Step 1: Update `model-routing.md` & `SKILL.md`**
- Replace `cs-ops` reliability-first default from `openai/gpt-5.4` to `openrouter/openai/gpt-5.6-luna` (primary) / `openrouter/openai/gpt-5.6-sol` (escalation).
- Update OpenCode `build` / `plan` / `solutions-architect` premium fallbacks from `openai/gpt-5.4` to `openrouter/openai/gpt-5.6-sol` or `openrouter/google/gemini-3.7-flash`.

**Step 2: Update `repo_dispatch_helper.py`**
- Change fallback model constants from `openai/gpt-5.4-mini` to `openrouter/openai/gpt-5.6-luna` or `openrouter/google/gemini-3.7-flash`.

**Step 3: Verification**
Run unit tests / smoke checks on `repo_dispatch_helper.py`:
```bash
python3 /Users/jason/.hermes/profiles/ops/skills/vault-opencode-dispatch/scripts/repo_dispatch_helper.py --repo /Users/jason/vault --intent planning --explain
```

---

### Task 5: End-to-End Verification Run

**Objective:** Verify that a live test probe across the updated dispatch and bridge routes executes cleanly, logs correct model telemetry, and returns the expected tokens.

**Step 1: OpenCode Dispatch Telemetry Probe**
Run a test wrapper probe for `cs-ops` using the new model routing ladder:
```bash
python /Users/jason/.hermes/profiles/ops/skills/vault-opencode-dispatch/scripts/opencode_dispatch.py \
  --request-summary "verification probe for cs-ops model-ops alignment" \
  --task-class verification \
  --source-surface desktop \
  --agent cs-ops \
  --model openrouter/openai/gpt-5.6-luna \
  --fallback-model openrouter/openai/gpt-5.6-sol \
  --status test \
  --prompt "Respond with exactly CSOPS_MODELOPS_OK"
```

**Step 2: Review Telemetry**
Verify that telemetry recorded the new model route without failures.
