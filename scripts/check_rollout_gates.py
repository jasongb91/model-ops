#!/usr/bin/env python3
"""
check_rollout_gates.py

Evaluates telemetry for all staged candidate models in staged_candidates.json
(or a specified model) across Hermes and OpenCode logs to determine if rollout gates
(Stage 2/3/4) are met.

Can output:
- JSON summary for scripting/reporting
- Slack block payload for delivery via `hermes -p ops-light send`
- Status markdown block for inclusion in daily scheduled briefings
"""

import json
import os
import re
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STAGED_CANDIDATES_PATH = REPO_ROOT / "staged_candidates.json"
HERMES_LOG_PATH = Path(os.path.expanduser("~/.hermes/profiles/ops/logs/agent.log"))
HERMES_ERRORS_PATH = Path(os.path.expanduser("~/.hermes/profiles/ops/logs/errors.log"))


def load_candidates():
    if STAGED_CANDIDATES_PATH.exists():
        try:
            with open(STAGED_CANDIDATES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("active_candidates", [])
        except Exception:
            pass
    return []


def parse_telemetry(candidate_info: dict, window_hours: int = 24):
    candidate_model = candidate_info.get("model_id", "")
    min_turns = candidate_info.get("thresholds", {}).get("min_turns", 10)
    max_error_rate = candidate_info.get("thresholds", {}).get("max_error_rate_pct", 0.0)

    cutoff = datetime.now() - timedelta(hours=window_hours)
    
    total_turns = 0
    total_errors = 0
    durations = []
    
    # 1. Parse agent.log for turn events & timings
    if HERMES_LOG_PATH.exists():
        with open(HERMES_LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                m_time = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                if not m_time:
                    continue
                try:
                    t = datetime.strptime(m_time.group(1), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
                if t < cutoff:
                    continue
                
                if candidate_model in line:
                    if "chat_completion" in line or "conversation_loop" in line or "session" in line:
                        total_turns += 1
                        m_dur = re.search(r"duration=([\d\.]+)s", line)
                        if m_dur:
                            durations.append(float(m_dur.group(1)))

    # 2. Parse errors.log for candidate model errors
    if HERMES_ERRORS_PATH.exists():
        with open(HERMES_ERRORS_PATH, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                m_time = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                if not m_time:
                    continue
                try:
                    t = datetime.strptime(m_time.group(1), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
                if t < cutoff:
                    continue
                
                if candidate_model in line and ("error" in line.lower() or "exception" in line.lower() or "failed" in line.lower()):
                    total_errors += 1

    avg_latency = round(sum(durations) / len(durations), 2) if durations else None
    error_rate = round((total_errors / total_turns * 100), 1) if total_turns > 0 else 0.0

    return {
        "candidate": candidate_model,
        "display_name": candidate_info.get("display_name", candidate_model),
        "current_stage": candidate_info.get("current_stage", 1),
        "target_lane": candidate_info.get("target_lane", "General"),
        "window_hours": window_hours,
        "total_turns": total_turns,
        "total_errors": total_errors,
        "error_rate_pct": error_rate,
        "avg_latency_s": avg_latency,
        "gate_stage2_ready": (total_turns >= min_turns and error_rate <= max_error_rate),
        "gate_stage3_ready": (total_turns >= (min_turns * 2) and error_rate <= 1.0),
        "timestamp": datetime.now().isoformat()
    }


def format_slack_card(results: list) -> str:
    if not results:
        return "⚡ *Model Promotion Gates:* No active candidates currently in staged evaluation."

    blocks = ["⚡ *Model Promotion Gate Review*"]
    for data in results:
        ready_s2 = "✅ READY" if data["gate_stage2_ready"] else "⏳ IN PROGRESS"
        turns = data["total_turns"]
        errs = data["total_errors"]
        lat = f"{data['avg_latency_s']}s" if data['avg_latency_s'] is not None else "n/a"
        cand = data["display_name"]
        model_id = data["candidate"]
        
        block = (
            f"\n*Candidate: {cand} (`{model_id}`)*\n"
            f"• Target Lane: {data['target_lane']} | Current Stage: {data['current_stage']}\n"
            f"• {data['window_hours']}h Telemetry: {turns} turns, {errs} errors ({data['error_rate_pct']}%), avg latency {lat}\n"
            f"• Stage 2 Gate: {ready_s2}\n"
        )
        if data["gate_stage2_ready"]:
            block += f"• *Action:* Criteria met. Reply `promote {model_id} stage2` to advance.\n"
        else:
            block += f"• *Action:* Insufficient interactive sample volume or errors detected. Retaining Stage {data['current_stage']}.\n"
        blocks.append(block)

    return "\n".join(blocks)


def format_briefing_block(results: list) -> str:
    if not results:
        return "### Model Promotion Gates\n- No active candidates currently in staged evaluation."

    lines = ["### Model Promotion Gates"]
    for data in results:
        ready_s2 = "GREEN (Ready)" if data["gate_stage2_ready"] else "HOLD (Gathering data)"
        turns = data["total_turns"]
        errs = data["total_errors"]
        cand = data["display_name"]
        model_id = data["candidate"]
        lines.append(
            f"- **{cand} (`{model_id}`)** [{data['target_lane']}]\n"
            f"  - Status: {ready_s2} | Current Stage: {data['current_stage']}\n"
            f"  - {data['window_hours']}h Observed Turns: {turns} | Errors: {errs} ({data['error_rate_pct']}%)\n"
            f"  - Next Action: Advance to Stage 2 once confirmed."
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check model rollout telemetry gates across active candidates.")
    parser.add_argument("--candidate", default=None, help="Specific candidate model ID (overrides staged_candidates.json)")
    parser.add_argument("--window", type=int, default=24, help="Evaluation window in hours")
    parser.add_argument("--format", choices=["json", "slack", "briefing"], default="json")
    parser.add_argument("--notify", action="store_true", help="Send Slack message via ops-light if any model is ready")
    args = parser.parse_args()

    candidates = []
    if args.candidate:
        candidates = [{"model_id": args.candidate, "display_name": args.candidate, "thresholds": {"min_turns": 10, "max_error_rate_pct": 0.0}}]
    else:
        candidates = load_candidates()

    results = [parse_telemetry(c, window_hours=args.window) for c in candidates]

    if args.format == "json":
        print(json.dumps(results, indent=2))
    elif args.format == "slack":
        print(format_slack_card(results))
    elif args.format == "briefing":
        print(format_briefing_block(results))

    if args.notify and any(r["gate_stage2_ready"] for r in results):
        slack_msg = format_slack_card(results)
        temp_path = Path("/tmp/model_rollout_gate.txt")
        temp_path.write_text(slack_msg, encoding="utf-8")
        os.system(f"hermes -p ops-light send --to slack:D0BJDD1JV3J --file {temp_path} >/dev/null 2>&1")


if __name__ == "__main__":
    main()
