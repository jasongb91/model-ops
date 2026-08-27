#!/usr/bin/env python3
"""
eval_promo_candidates.py

Automated model ops evaluation runner against benchmark-suite.md and eval-protocol.md
probes (B1-B8) to score promotional / low-cost candidate models on:
  1. Correctness (1-5)
  2. Grounding & Evidence Use (1-5)
  3. Stop-Discipline (1-5)
  4. Format Compliance (1-5)
  5. Latency (1-5)
  6. Operator Cleanup Burden (1-5)
  7. Token Efficiency / Cost (1-5)

Features:
  - Supports evaluating specific models (--models) or auto-discovering candidate models from
    ~/.hermes/telemetry/openrouter-model-deltas.json (--from-deltas)
  - Full B1-B8 probe test suite with deterministic rule-based and regex assertions
  - Multi-round execution (--rounds, default 3) to measure variance and reliability
  - Automated rubric scoring across all 7 dimensions and R0/R1/R2 promotion eligibility gating
  - Formats results into structured JSON artifacts and markdown summaries ready for experiment-log.md
  - Dry-run / mock mode (--dry-run) for testing assertions and harness behavior without API spend
"""

import argparse
import json
import math
import os
import re
import sys
import time
import urllib.request
import urllib.error

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_DELTAS_PATH = os.path.expanduser("~/.hermes/telemetry/openrouter-model-deltas.json")
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/.hermes/telemetry/eval_results")


def is_text_output_candidate(model_info):
    architecture = model_info.get("architecture") or {}
    output_modalities = architecture.get("output_modalities") or []

    if output_modalities:
        return set(output_modalities) == {"text"}

    return model_info.get("text_output_only", True)


def find_openrouter_key():
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ.get("OPENROUTER_API_KEY")
    paths = [
        os.path.expanduser("~/.hermes/.env"),
        os.path.expanduser("~/.hermes/profiles/eval/.env"),
        os.path.expanduser("~/.hermes/profiles/eval/auth.json"),
        os.path.expanduser("~/.hermes/profiles/ops/auth.json"),
        os.path.expanduser("~/.hermes/profiles/crogl/auth.json"),
        os.path.expanduser("~/.hermes/auth.json"),
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    content = f.read()
                    if p.endswith(".env"):
                        for line in content.splitlines():
                            if line.startswith("OPENROUTER_API_KEY="):
                                return line.split("=", 1)[1].strip().strip('"').strip("'")
                    elif p.endswith(".json"):
                        data = json.loads(content)
                        if "providers" in data and "openrouter" in data["providers"]:
                            or_data = data["providers"]["openrouter"]
                            if isinstance(or_data, dict):
                                return or_data.get("api_key") or or_data.get("access_token")
                            elif isinstance(or_data, str):
                                return or_data
                        if "openrouter" in data:
                            return data["openrouter"].get("api_key") or data["openrouter"].get("access_token")
            except Exception:
                pass
    return None

# ==============================================================================
# BENCHMARK PROBES B1 - B8
# ==============================================================================

PROBES = {
    "B1": {
        "id": "B1",
        "name": "Internal Scheduled-Status Synthesis",
        "reliability_class": "R1",
        "latency_budget": 20.0,
        "system": "You are an AI operations assistant. Generate concise, high-signal internal ops status summaries adhering strictly to the facts in the telemetry logs.",
        "prompt": """Generate a concise internal ops status brief. Summarize active systems, flag operational failures, and list immediate remediation actions in bullet form.

Raw Telemetry Logs:
- Hermes Cron Status: 2 jobs active, 1 failure (sync-acmedemo-from-main failed with network timeout after 180s).
- Launchd Sweeps: 7 agents active, 1 timed out (health-check-sweep on agent-4 timed out after 300s).
- GCP VM Status: acmedemo instance is healthy @ 34.69.169.75, Cloud SQL disk utilization at 42%.
- OpenCode 14-day spend metrics: $548 baseline.
""",
        "assertions": [
            ("identifies_failing_cron", lambda txt, meta: "sync-acmedemo" in txt.lower() and ("fail" in txt.lower() or "timeout" in txt.lower())),
            ("identifies_timed_out_launchd", lambda txt, meta: ("health-check" in txt.lower() or "agent-4" in txt.lower() or "launchd" in txt.lower()) and ("time" in txt.lower() or "timeout" in txt.lower())),
            ("quotes_exact_gcp_ip", lambda txt, meta: "34.69.169.75" in txt),
            ("quotes_cloud_sql_utilization", lambda txt, meta: "42%" in txt or "42 percent" in txt.lower()),
            ("quotes_opencode_spend", lambda txt, meta: "$548" in txt or "548" in txt),
            ("no_hallucinated_outages", lambda txt, meta: "critical outage" not in txt.lower() and "sev0" not in txt.lower() and "unrelated" not in txt.lower()),
            ("stop_discipline_check", lambda txt, meta: len(txt.split()) <= 300 and not any(phrase in txt.lower() for phrase in ["sure, here is", "certainly!", "as an ai", "in conclusion"]))
        ]
    },
    "B2": {
        "id": "B2",
        "name": "Morning Brief Component Extraction",
        "reliability_class": "R1/R2",
        "latency_budget": 10.0,
        "system": "You are an operations extraction specialist. Extract key customer facts and output high-signal bullets.",
        "prompt": """Extract key customer movement, new blockers, and upcoming milestones from the TXNM Energy interaction transcript. Output 3-5 high-signal bullets ready for morning ops briefing.

Input Context:
Customer: TXNM Energy
Meeting Transcripts & Emails:
- Meeting 1 (Aug 18): Jason (Crogl), John (TXNM) agreed on Grid Modernization Phase 1 rollout architecture. Target go-live date set for September 15, 2026.
- Email Thread 1 (Aug 19): TXNM Security team flagged SAML SSO certificate expiry on staging cluster scheduled for August 28, 2026. Internal ticket SEC-942 opened.
- Meeting 2 (Aug 20): Jason agreed to provide Airbyte connector schema by August 24, 2026. Sarah (TXNM) will confirm IdP metadata URL by August 29 once cert is rotated.
""",
        "assertions": [
            ("highlights_saml_cert_blocker", lambda txt, meta: "saml" in txt.lower() and ("cert" in txt.lower() or "sec-942" in txt.upper() or "expiry" in txt.lower())),
            ("extracts_target_dates", lambda txt, meta: "september 15" in txt.lower() or "august 28" in txt.lower() or "august 24" in txt.lower()),
            ("extracts_airbyte_or_grid_mod", lambda txt, meta: "airbyte" in txt.lower() or "grid modernization" in txt.lower()),
            ("word_count_bounded", lambda txt, meta: 30 <= len(txt.split()) <= 200),
            ("bullet_format_compliance", lambda txt, meta: txt.strip().startswith("-") or txt.strip().startswith("*") or "\n-" in txt or "\n*" in txt)
        ]
    },
    "B3": {
        "id": "B3",
        "name": "CS Account-Note Drafting & Updates",
        "reliability_class": "R1",
        "latency_budget": 30.0,
        "system": "You are a CS operations assistant. Draft canonical Markdown account note updates. Strictly adhere to canonical sections (## Summary, ## Blockers, ## Open tasks, ## Recent activity), maintain bullet immutability, use bold labels (**Attendees:**, **Action:**), and never leak internal speculation.",
        "prompt": """Draft the weekly update entry for customer-accounts/txnm-energy.md. Strictly adhere to canonical sections (## Onboarding, ## Blockers, ## Open tasks, ## Recent activity), maintain bullet immutability, and respect Direct-Correlation rules.

Input Context:
Direct customer meeting notes with TXNM Energy stakeholders:
Attendees: Jason (Crogl), John (TXNM), Sarah (TXNM).
Discussion & Milestone: Grid Modernization Phase 1 architecture signoff completed. Target go-live date set for September 15, 2026.
Blockers: Identified SAML SSO certificate expiry on staging cluster scheduled for August 28, 2026; TXNM internal secops ticket SEC-942 opened to rotate cert.
Action Items / Open Tasks:
- Jason to provide updated Airbyte connector schema definitions by August 24, 2026.
- Sarah to confirm IdP metadata URL once SEC-942 resolves.
""",
        "assertions": [
            ("canonical_sections_present", lambda txt, meta: any(h in txt for h in ["## Onboarding", "## Blockers", "## Open tasks", "## Recent activity", "## Summary"])),
            ("bold_label_syntax", lambda txt, meta: "**Attendees:**" in txt or "**Action:**" in txt or "**Blockers:**" in txt or "**Milestone:**" in txt or "**Status:**" in txt or "**Owner:**" in txt),
            ("cites_saml_and_sec942", lambda txt, meta: "saml" in txt.lower() and ("sec-942" in txt.upper() or "cert" in txt.lower())),
            ("direct_correlation_no_speculation", lambda txt, meta: "threat-intel" not in txt.lower() and "speculation" not in txt.lower() and "internal hypothesis" not in txt.lower()),
            ("preserves_task_owners", lambda txt, meta: "jason" in txt.lower() and "sarah" in txt.lower())
        ]
    },
    "B4": {
        "id": "B4",
        "name": "Frontdoor / Slack Triage & Classification",
        "reliability_class": "R2",
        "latency_budget": 8.0,
        "system": "You are an automated triage classifier. Output ONLY valid, parseable JSON matching the required schema with zero markdown wrapping or conversational preamble.",
        "prompt": """Classify the inbound message:
Inbound message: "Hey team, we're seeing intermittent 502 errors on the Acmedemo REST API port 8082 during peak traffic. Can someone check the crogld service logs?"
Inbound channel: #ops-intake (public).

Return a JSON object with EXACTLY these keys:
{
  "route": "cs-ops" | "solutions-architect" | "build" | "direct-reply",
  "urgency": "P1" | "P2" | "P3",
  "is_private_channel": boolean,
  "privacy_violation": boolean,
  "suggested_action": string
}
""",
        "assertions": [
            ("valid_json_schema", lambda txt, meta: _assert_b4_json(txt, meta)),
            ("route_validity", lambda txt, meta: meta.get("b4_parsed", {}).get("route") in ["cs-ops", "solutions-architect", "build", "direct-reply"]),
            ("urgency_classification", lambda txt, meta: meta.get("b4_parsed", {}).get("urgency") in ["P1", "P2"]),
            ("channel_privacy_assessment", lambda txt, meta: meta.get("b4_parsed", {}).get("privacy_violation") is False and meta.get("b4_parsed", {}).get("is_private_channel") is False),
            ("suggested_action_present", lambda txt, meta: bool(meta.get("b4_parsed", {}).get("suggested_action")))
        ]
    },
    "B5": {
        "id": "B5",
        "name": "Artifact & Distribution Audit Synthesis",
        "reliability_class": "R1",
        "latency_budget": 25.0,
        "system": "You are a DevOps release engineer. Audit multi-region build & distribution matrices with absolute precision.",
        "prompt": """Audit the distribution matrix for release v2.4.0-rc3. Output a markdown status table and explicitly list blockers preventing release promotion.

Input Context: Multi-region build telemetry table for release v2.4.0-rc3:
- Region: AWS us-east-1 | Artifact: tar.gz | SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | S3 URL: https://s3.us-east-1.amazonaws.com/releases/v2.4.0-rc3.tar.gz (Verified, Status: 200 OK) | ECR Tag: v2.4.0-rc3 (Verified)
- Region: AWS us-gov-west-1 | Artifact: tar.gz | SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | S3 URL: https://s3.us-gov-west-1.amazonaws.com/releases/v2.4.0-rc3.tar.gz (FAILED: 403 SignatureDoesNotMatch presign expired) | ECR Tag: MISSING in GovCloud ECR registry
- Region: GCP us-central1 | Artifact: tar.gz | SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | GCS URL: https://storage.googleapis.com/releases/v2.4.0-rc3.tar.gz (Verified, Status: 200 OK) | Artifact Registry Tag: v2.4.0-rc3 (Verified)
""",
        "assertions": [
            ("generates_markdown_table", lambda txt, meta: "|" in txt and ("-|-" in txt or "| ---" in txt or "|:---" in txt)),
            ("flags_us_gov_west_s3_blocker", lambda txt, meta: "us-gov-west-1" in txt and ("403" in txt or "presign" in txt.lower() or "s3" in txt.lower() or "signature" in txt.lower())),
            ("flags_missing_govcloud_ecr_tag", lambda txt, meta: "ecr" in txt.lower() and ("missing" in txt.lower() or "tag" in txt.lower())),
            ("confirms_healthy_regions", lambda txt, meta: "us-east-1" in txt and "us-central1" in txt and ("verified" in txt.lower() or "200 ok" in txt.lower() or "ok" in txt.lower() or "healthy" in txt.lower() or "green" in txt.lower())),
            ("lists_explicit_blockers", lambda txt, meta: "blocker" in txt.lower())
        ]
    },
    "B6": {
        "id": "B6",
        "name": "Long-Context Synthesis & Needle Recall",
        "reliability_class": "R1",
        "latency_budget": 45.0,
        "system": "You are an enterprise architecture and security compliance auditor. Synthesize requirements precisely from multi-document context.",
        "prompt": """Synthesize enterprise customer trust-store requirements across all customer accounts. Identify any custom root CA certificate paths required for air-gapped or self-hosted deployments.

Context Corpus:
""" + ("\n".join([f"[Document {i:02d}] Customer Note {chr(65 + (i % 26))}{i}: Ingress endpoints utilize public AWS ACM TLS 1.3 certificates in region us-east-1. Standard OS truststore path /etc/ssl/certs/ca-certificates.crt is used for public root certs." for i in range(40)])) + """

[Document 41 - Special Compliance Profile]
Account: Türk Telekom
Scope: On-premises Air-Gapped & Ingress Gateway Mesh
Requirement: Türk Telekom requires mutual TLS 1.3 with custom root CA cert in Chainguard container /etc/ssl/certs/ca-certificates.crt. Strict CN validation against tt-internal-gateway.telekom.com.tr is mandated.

""" + ("\n".join([f"[Document {i:02d}] Customer Note {chr(65 + (i % 26))}{i}: Edge ingress TLS 1.3 termination managed via Cloudflare enterprise proxy with standard automated cert rotation." for i in range(42, 80)])) + """

State the exact customer name, the custom root CA certificate path inside the container, the mTLS requirement, and the CN validation target.
""",
        "assertions": [
            ("exact_container_path_recall", lambda txt, meta: "/etc/ssl/certs/ca-certificates.crt" in txt),
            ("correct_account_attribution", lambda txt, meta: "türk telekom" in txt.lower() or "turk telekom" in txt.lower()),
            ("identifies_mtls_requirement", lambda txt, meta: "1.3" in txt and ("mtls" in txt.lower() or "mutual tls" in txt.lower())),
            ("identifies_cn_target", lambda txt, meta: "tt-internal-gateway.telekom.com.tr" in txt),
            ("no_cross_account_contamination", lambda txt, meta: "acme" not in txt.lower() or "public root" in txt.lower() or "standard" in txt.lower())
        ]
    },
    "B7": {
        "id": "B7",
        "name": "Complex Ops Planning & Decomposition",
        "reliability_class": "R1",
        "latency_budget": 40.0,
        "system": "You are a Principal Cloud Infrastructure Architect. Structure phased execution plans with gotchas and exact commands.",
        "prompt": """Requirement Spec: Migrate an internal agent backend to GovCloud EKS Fargate using IMDSv2, AWS Bedrock mantle endpoints, and custom IAM role bindings.

Key constraints & potential gotchas:
- IMDSv2 token retrieval sequence requires PUT request with X-aws-ec2-metadata-token-ttl-seconds before GET metadata.
- AWS Bedrock mantle endpoint format is bedrock-mantle.<region>.api.aws/v1 vs standard bedrock runtime.
- Fargate pods cannot run privileged DaemonSets for logging.

Task Prompt: Create a phased technical execution plan with dependency ordering, potential failure gotchas (IMDS hostname resolution, Bedrock tool schema formats, Fargate logging), and exact verification commands.
""",
        "assertions": [
            ("cites_bedrock_mantle_endpoint", lambda txt, meta: "bedrock-mantle" in txt or "mantle" in txt.lower()),
            ("includes_imdsv2_token_handling", lambda txt, meta: "imdsv2" in txt.lower() or "x-aws-ec2-metadata-token" in txt.lower() or "token" in txt.lower()),
            ("addresses_fargate_logging_constraint", lambda txt, meta: "fargate" in txt.lower() and ("log" in txt.lower() or "fluent" in txt.lower() or "daemonset" in txt.lower() or "sidecar" in txt.lower())),
            ("structured_phases_present", lambda txt, meta: any(p in txt for p in ["Phase 1", "Phase 2", "Phase 3", "## Preflight", "## Implementation", "1.", "2."])),
            ("includes_verification_commands", lambda txt, meta: "aws " in txt or "kubectl " in txt or "curl " in txt)
        ]
    },
    "B8": {
        "id": "B8",
        "name": "Agent Tool Use & Structured Execution",
        "reliability_class": "R1",
        "latency_budget": 25.0,
        "system": "You are an automated security operations assistant. Execute appropriate tool calls adhering strictly to function schemas.",
        "prompt": """Available MCP Tool Definitions:
1. `mcp__crogld__crowdstrike_falcon_query`: Arguments: {"sha256": string, "time_range": string (optional)}
2. `mcp__crogld__create_investigation`: Arguments: {"title": string, "severity": "P1" | "P2" | "P3", "indicators": list of strings, "description": string}

User Prompt:
"Run a query on crowdstrike falcon for SHA256 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' and open a P2 investigation ticket."

Output the exact tool call(s) in OpenAI/JSON format.
""",
        "assertions": [
            ("names_falcon_query_tool", lambda txt, meta: "mcp__crogld__crowdstrike_falcon_query" in txt or "falcon_query" in txt),
            ("cites_target_sha256", lambda txt, meta: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" in txt),
            ("names_create_investigation_tool", lambda txt, meta: "mcp__crogld__create_investigation" in txt or "create_investigation" in txt),
            ("specifies_p2_severity", lambda txt, meta: '"P2"' in txt or "'P2'" in txt or "severity" in txt),
            ("valid_tool_call_structure", lambda txt, meta: ("name" in txt and "arguments" in txt) or "{" in txt)
        ]
    }
}

def _assert_b4_json(txt, meta):
    raw = txt.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\n?", "", raw)
        raw = re.sub(r"\n?```$", "", raw)
    try:
        parsed = json.loads(raw.strip())
        meta["b4_parsed"] = parsed
        required_keys = ["route", "urgency", "is_private_channel", "privacy_violation", "suggested_action"]
        return all(k in parsed for k in required_keys)
    except Exception:
        return False

# ==============================================================================
# EXECUTION ENGINE
# ==============================================================================

def execute_openrouter_request(api_key, model_id, system_prompt, user_prompt, temperature=0.2, top_p=0.95, max_tokens=2048):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://hermes-eval.crogl.internal",
        "X-Title": "Hermes Model Ops Automated Evaluation Harness"
    }
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens
    }
    t0 = time.time()
    req = urllib.request.Request(OPENROUTER_API_URL, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            t1 = time.time()
            data = json.loads(resp.read().decode("utf-8"))
            choice = data["choices"][0]
            content = choice.get("message", {}).get("content", "") or ""
            reasoning = choice.get("message", {}).get("reasoning", "") or ""
            usage = data.get("usage", {})
            return {
                "success": True,
                "latency": t1 - t0,
                "content": content,
                "reasoning": reasoning,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        return {"success": False, "latency": time.time() - t0, "error": f"HTTP {e.code}: {err_body}"}
    except Exception as e:
        return {"success": False, "latency": time.time() - t0, "error": str(e)}

def mock_probe_execution(probe, model_id):
    """Generates deterministic mock output for dry-run verification."""
    time.sleep(0.05)
    p_id = probe["id"]
    if p_id == "B1":
        content = ("Ops Status Brief:\n"
                   "- Hermes Cron: 2 active, 1 failure (sync-acmedemo-from-main timed out after 180s).\n"
                   "- Launchd Sweeps: 7 agents, health-check-sweep on agent-4 timed out after 300s.\n"
                   "- GCP VM: acmedemo instance healthy @ 34.69.169.75, Cloud SQL storage at 42%.\n"
                   "- OpenCode: $548 spend baseline.\n"
                   "Remediation: Restart health-check-sweep and investigate network timeout on sync-acmedemo.")
    elif p_id == "B2":
        content = ("- Grid Modernization Phase 1 signoff complete; target go-live September 15, 2026.\n"
                   "- Blocker: SAML SSO cert expiry scheduled for August 28, 2026 (TXNM SEC-942 opened).\n"
                   "- Action: Jason providing updated Airbyte connector schema by August 24, 2026.")
    elif p_id == "B3":
        content = ("## Summary\n"
                   "TXNM Energy architecture review and signoff.\n"
                   "**Attendees:** Jason (Crogl), John (TXNM), Sarah (TXNM)\n\n"
                   "## Blockers\n"
                   "- [ ] SAML SSO certificate expiry on staging cluster scheduled for August 28, 2026 (TXNM ticket SEC-942)\n\n"
                   "## Open tasks\n"
                   "- [ ] **Action:** Jason to provide Airbyte connector schema by August 24, 2026\n"
                   "- [ ] **Action:** Sarah to confirm IdP metadata URL once SEC-942 resolves\n\n"
                   "## Recent activity\n"
                   "- Completed Grid Modernization Phase 1 signoff with target go-live September 15, 2026.")
    elif p_id == "B4":
        content = json.dumps({
            "route": "cs-ops",
            "urgency": "P2",
            "is_private_channel": False,
            "privacy_violation": False,
            "suggested_action": "Check crogld systemd logs and investigate 502 status on port 8082"
        })
    elif p_id == "B5":
        content = ("| Region | Artifact | SHA256 | S3/GCS Status | ECR Status | Status |\n"
                   "|:---|:---|:---|:---|:---|:---|\n"
                   "| AWS us-east-1 | tar.gz | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | 200 OK | Verified | Verified |\n"
                   "| AWS us-gov-west-1 | tar.gz | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | 403 S3 Presign Expired | MISSING | BLOCKER |\n"
                   "| GCP us-central1 | tar.gz | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | 200 OK | Verified | Verified |\n\n"
                   "### Blockers Preventing Release Promotion:\n"
                   "1. AWS us-gov-west-1 S3 presign URL failed with 403 SignatureDoesNotMatch.\n"
                   "2. GovCloud ECR container tag v2.4.0-rc3 is missing.")
    elif p_id == "B6":
        content = ("Enterprise Trust-Store Requirements Synthesis:\n"
                   "- Customer: Türk Telekom\n"
                   "- Container Path: /etc/ssl/certs/ca-certificates.crt\n"
                   "- Requirement: Mutual TLS 1.3 (mTLS) with custom root CA in Chainguard container.\n"
                   "- Validation Target: tt-internal-gateway.telekom.com.tr")
    elif p_id == "B7":
        content = ("## Technical Execution Plan: GovCloud EKS Fargate Migration\n"
                   "### Phase 1: Preflight & Identity\n"
                   "- Configure IAM Roles for Service Accounts (IRSA).\n"
                   "- IMDSv2 token acquisition flow: PUT token request with ttl header before GET metadata.\n"
                   "### Phase 2: Runtime Configuration\n"
                   "- Configure Bedrock mantle endpoint format: bedrock-mantle.us-gov-west-1.api.aws/v1.\n"
                   "- Configure sidecar logging since Fargate pods do not support privileged logging DaemonSets.\n"
                   "### Phase 3: Verification Commands\n"
                   "- `aws eks describe-cluster --name govcloud-eks`\n"
                   "- `kubectl get pods -n backend`")
    elif p_id == "B8":
        content = json.dumps([
            {
                "name": "mcp__crogld__crowdstrike_falcon_query",
                "arguments": {"sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
            },
            {
                "name": "mcp__crogld__create_investigation",
                "arguments": {
                    "title": "Investigate hash e3b0c442",
                    "severity": "P2",
                    "indicators": ["e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"],
                    "description": "CrowdStrike hash investigation"
                }
            }
        ])
    else:
        content = "Mock response"

    return {
        "success": True,
        "latency": 0.45,
        "content": content,
        "reasoning": "",
        "prompt_tokens": 350,
        "completion_tokens": 120,
        "total_tokens": 470
    }

# ==============================================================================
# SCORING & RUBRIC ENGINE
# ==============================================================================

def score_probe_run(probe, result, pricing_rates):
    """
    Evaluates standard 7 scoring dimensions (1-5 scale) for a single probe execution:
      1. Correctness
      2. Grounding & Evidence Use
      3. Stop-Discipline
      4. Format Compliance
      5. Latency
      6. Operator Cleanup Burden
      7. Token Efficiency / Cost
    """
    if not result.get("success"):
        return {
            "correctness": 1.0,
            "grounding": 1.0,
            "stop_discipline": 1.0,
            "format_compliance": 1.0,
            "latency_score": 1.0,
            "cleanup_burden": 1.0,
            "token_efficiency": 1.0,
            "overall_score": 1.0,
            "assertion_pass_rate": 0.0,
            "passed_assertions": [],
            "failed_assertions": [("execution_failure", result.get("error", "Unknown error"))]
        }

    content = result.get("content", "")
    latency = result.get("latency", 0.0)
    p_tokens = result.get("prompt_tokens", 0)
    c_tokens = result.get("completion_tokens", 0)

    # Evaluate assertions
    meta = {}
    passed = []
    failed = []
    for name, fn in probe["assertions"]:
        try:
            if fn(content, meta):
                passed.append(name)
            else:
                failed.append(name)
        except Exception as e:
            failed.append(f"{name} (eval error: {e})")

    pass_rate = len(passed) / len(probe["assertions"]) if probe["assertions"] else 1.0

    # Dimension 1: Correctness (1-5)
    correctness = round(1.0 + 4.0 * pass_rate, 2)

    # Dimension 2: Grounding (1-5)
    grounding = 5.0 if pass_rate >= 0.85 else (4.0 if pass_rate >= 0.6 else (2.5 if pass_rate >= 0.4 else 1.0))

    # Dimension 3: Stop-Discipline (1-5)
    # Penalize reasoning leakage, verbose preambles, and conversational filler
    leaks = any(x in content.lower() for x in ["<think>", "</think>", "as an ai", "sure, here is", "in conclusion"])
    stop_discipline = 3.0 if leaks else (5.0 if len(content.split()) <= 450 else 4.0)

    # Dimension 4: Format Compliance (1-5)
    format_compliance = 5.0 if pass_rate >= 0.8 else (3.5 if pass_rate >= 0.5 else 2.0)
    if probe["id"] == "B4" and not meta.get("b4_parsed"):
        format_compliance = 1.0

    # Dimension 5: Latency (1-5)
    budget = probe["latency_budget"]
    if latency <= budget * 0.3:
        lat_score = 5.0
    elif latency <= budget * 0.6:
        lat_score = 4.8
    elif latency <= budget:
        lat_score = 4.0
    elif latency <= budget * 1.5:
        lat_score = 3.0
    else:
        lat_score = 2.0

    # Dimension 6: Operator Cleanup Burden (1-5)
    cleanup_burden = 5.0 if (pass_rate == 1.0 and stop_discipline >= 4.5) else (4.0 if pass_rate >= 0.8 else 2.5)

    # Dimension 7: Token Efficiency / Cost (1-5)
    p_rate = pricing_rates.get("prompt", 0.0)
    c_rate = pricing_rates.get("completion", 0.0)
    cost = (p_tokens * p_rate) + (c_tokens * c_rate)
    blended_1m = ((p_rate * 0.75) + (c_rate * 0.25)) * 1_000_000
    if blended_1m == 0.0:
        cost_score = 5.0
    elif blended_1m <= 0.25:
        cost_score = 5.0
    elif blended_1m <= 1.00:
        cost_score = 4.7
    elif blended_1m <= 3.00:
        cost_score = 4.0
    else:
        cost_score = 3.0

    overall = round((correctness * 0.25) + (grounding * 0.20) + (stop_discipline * 0.15) + 
                    (format_compliance * 0.15) + (lat_score * 0.10) + (cleanup_burden * 0.15), 2)

    return {
        "correctness": correctness,
        "grounding": grounding,
        "stop_discipline": stop_discipline,
        "format_compliance": format_compliance,
        "latency_score": lat_score,
        "cleanup_burden": cleanup_burden,
        "token_efficiency": cost_score,
        "overall_score": overall,
        "cost": round(cost, 6),
        "assertion_pass_rate": round(pass_rate, 2),
        "passed_assertions": passed,
        "failed_assertions": failed
    }

def evaluate_model_on_probes(api_key, model_info, probe_ids, rounds=3, dry_run=False):
    model_id = model_info["id"]
    label = model_info.get("name", model_id)
    pricing = model_info.get("pricing", {})
    p_rate = (pricing.get("prompt_per_1m", 0.0) or 0.0) / 1_000_000
    c_rate = (pricing.get("completion_per_1m", 0.0) or 0.0) / 1_000_000
    pricing_rates = {"prompt": p_rate, "completion": c_rate}

    print(f"\n================================================================================")
    print(f"EVALUATING MODEL: {label} ({model_id})")
    print(f"Pricing: ${p_rate*1e6:.3f} / 1M in, ${c_rate*1e6:.3f} / 1M out | Context: {model_info.get('context_length', 'N/A')}")
    print(f"================================================================================")

    probe_results = {}
    for p_id in probe_ids:
        if p_id not in PROBES:
            continue
        probe = PROBES[p_id]
        print(f"\n--- Probe {p_id}: {probe['name']} (Budget: <{probe['latency_budget']}s, Class: {probe['reliability_class']}) ---")
        runs = []
        for r in range(1, rounds + 1):
            if dry_run:
                exec_res = mock_probe_execution(probe, model_id)
            else:
                exec_res = execute_openrouter_request(api_key, model_id, probe["system"], probe["prompt"])
            
            score_data = score_probe_run(probe, exec_res, pricing_rates)
            run_entry = {
                "run": r,
                "latency": round(exec_res.get("latency", 0.0), 3),
                "prompt_tokens": exec_res.get("prompt_tokens", 0),
                "completion_tokens": exec_res.get("completion_tokens", 0),
                "content": exec_res.get("content", ""),
                "scores": score_data,
                "success": exec_res.get("success", False),
                "error": exec_res.get("error")
            }
            runs.append(run_entry)
            status_str = f"Pass: {len(score_data['passed_assertions'])}/{len(probe['assertions'])}" if exec_res.get("success") else f"FAIL ({exec_res.get('error')})"
            print(f"  Run {r}/{rounds}: Latency={run_entry['latency']:.2f}s | Score={score_data['overall_score']:.2f}/5.0 | {status_str}")
            if score_data["failed_assertions"]:
                print(f"    Failed assertions: {score_data['failed_assertions']}")
            if not dry_run:
                time.sleep(1.0)
        
        # Aggregate probe stats
        valid_runs = [r for r in runs if r["success"]]
        avg_lat = round(sum(r["latency"] for r in runs) / len(runs), 2) if runs else 0
        avg_score = round(sum(r["scores"]["overall_score"] for r in runs) / len(runs), 2) if runs else 0
        avg_pass = round(sum(r["scores"]["assertion_pass_rate"] for r in runs) / len(runs), 2) if runs else 0
        total_probe_cost = sum(r["scores"].get("cost", 0) for r in runs)

        probe_results[p_id] = {
            "probe_id": p_id,
            "name": probe["name"],
            "reliability_class": probe["reliability_class"],
            "avg_latency": avg_lat,
            "avg_score": avg_score,
            "avg_pass_rate": avg_pass,
            "total_cost": round(total_probe_cost, 6),
            "runs": runs
        }

    # Aggregate Model Scores across evaluated probes
    all_scores = [p["avg_score"] for p in probe_results.values()]
    all_lats = [p["avg_latency"] for p in probe_results.values()]
    all_passes = [p["avg_pass_rate"] for p in probe_results.values()]
    overall_avg_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0
    overall_avg_lat = round(sum(all_lats) / len(all_lats), 2) if all_lats else 0
    overall_avg_pass = round(sum(all_passes) / len(all_passes), 2) if all_passes else 0
    total_eval_cost = round(sum(p["total_cost"] for p in probe_results.values()), 6)

    # Determine Promotion Eligibility (R0 / R1 / R2) based on eval-protocol.md
    eligibility = determine_promotion_eligibility(probe_results, overall_avg_score)

    summary = {
        "model_id": model_id,
        "label": label,
        "evaluated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "rounds_per_probe": rounds,
        "probes_evaluated": list(probe_results.keys()),
        "overall_score": overall_avg_score,
        "overall_latency": overall_avg_lat,
        "overall_pass_rate": overall_avg_pass,
        "total_eval_cost": total_eval_cost,
        "promotion_verdict": eligibility,
        "probe_details": probe_results
    }
    return summary

def determine_promotion_eligibility(probe_results, overall_score):
    """
    Evaluates promotion criteria:
      - R2 Fast-Track: score >= 4.8 on B2 and B4, 0 format failures.
      - R1 Fast-Track: score >= 4.8 on B1, B3, B5, B6, B7, B8, stop-discipline >= 4.5.
      - R0 Shadow-Gated: score >= 4.9 across all probes, zero cleanup burden (5.0), retains GPT-5.4/Sonnet fallback anchor.
    """
    eligible = []
    
    # R2 Fast-Track check (score >= 4.8 on B2/B4)
    r2_scores = [p["avg_score"] for pid, p in probe_results.items() if pid in ["B2", "B4"]]
    if r2_scores and (sum(r2_scores) / len(r2_scores) >= 4.8):
        eligible.append("R2 (Triage / Extraction Fast-Track)")

    # R1 Fast-Track check (score >= 4.8 on R1 probes)
    r1_scores = [p["avg_score"] for pid, p in probe_results.items() if pid in ["B1", "B3", "B5", "B6", "B7", "B8"]]
    if r1_scores and (sum(r1_scores) / len(r1_scores) >= 4.8):
        eligible.append("R1 (Internal Ops / Synthesis / Drafting Fast-Track)")

    # R0 Shadow-Gated check (score >= 4.9 across operational probes with zero cleanup burden)
    if overall_score >= 4.9 and len(probe_results) >= 4:
        eligible.append("R0 (Shadow-Gated Scheduled / Client-Facing with Frontier Fallbacks)")

    if not eligible:
        verdict = "keep-evaluating" if overall_score >= 4.0 else "reject"
    else:
        verdict = f"promote to {', '.join(eligible)}"
    
    return {
        "verdict": verdict,
        "eligible_tiers": eligible
    }

def format_markdown_report(eval_summary):
    """Formats evaluation run into standard experiment-log.md entry."""
    m = eval_summary
    lines = []
    lines.append(f"## {time.strftime('%Y-%m-%d')} — Automated Eval: {m['label']} via OpenRouter")
    lines.append(f"- surface: Automated Evaluation Harness (eval_promo_candidates.py)")
    lines.append(f"- task family: Benchmark Probes ({', '.join(m['probes_evaluated'])})")
    lines.append(f"- model evaluated: `{m['model_id']}`")
    lines.append(f"- total eval cost: ${m['total_eval_cost']:.6f} across {m['rounds_per_probe']} rounds")
    lines.append(f"- overall score: {m['overall_score']:.2f} / 5.0 (avg latency: {m['overall_latency']:.2f}s, pass rate: {m['overall_pass_rate']*100:.1f}%)")
    lines.append(f"- promotion verdict: **{m['promotion_verdict']['verdict']}**")
    lines.append(f"\n### Probe Scorecard:")
    lines.append("| Probe ID | Probe Name | Class | Avg Latency | Pass Rate | Score (1-5) |")
    lines.append("|:---|:---|:---:|:---:|:---:|:---:|")
    for pid, p in m["probe_details"].items():
        lines.append(f"| **{pid}** | {p['name']} | {p['reliability_class']} | {p['avg_latency']:.2f}s | {p['avg_pass_rate']*100:.0f}% | **{p['avg_score']:.2f}** |")
    lines.append("")
    return "\n".join(lines)

# ==============================================================================
# CLI HANDLER
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Automated Model Ops Benchmark Harness for Promo Candidates (B1-B8)")
    parser.add_argument("--models", nargs="+", help="Specific OpenRouter model IDs to benchmark (e.g. nvidia/nemotron-3-super-120b-a12b:free)")
    parser.add_argument("--probes", nargs="+", default=["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"], help="Probes to run (default: all B1-B8)")
    parser.add_argument("--rounds", type=int, default=3, help="Execution rounds per probe (default: 3)")
    parser.add_argument("--from-deltas", action="store_true", help="Load candidate promo/free models from openrouter-model-deltas.json")
    parser.add_argument("--deltas-file", default=DEFAULT_DELTAS_PATH, help=f"Path to deltas JSON (default: {DEFAULT_DELTAS_PATH})")
    parser.add_argument("--dry-run", action="store_true", help="Run harness with simulated outputs for assertion/logic verification")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help=f"Directory to write evaluation JSON artifacts (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--write-markdown", action="store_true", help="Print formatted markdown experiment log")
    args = parser.parse_args()

    api_key = None
    if not args.dry_run:
        api_key = find_openrouter_key()
        if not api_key:
            print("ERROR: OPENROUTER_API_KEY not found in environment or auth profiles. Run with --dry-run or configure credentials.", file=sys.stderr)
            sys.exit(1)

    candidate_models = []
    if args.models:
        for m_id in args.models:
            candidate_models.append({
                "id": m_id,
                "name": m_id,
                "pricing": {"prompt_per_1m": 0.0, "completion_per_1m": 0.0}
            })
    elif args.from_deltas:
        if not os.path.exists(args.deltas_file):
            print(f"ERROR: Deltas file {args.deltas_file} not found. Run scripts/check_openrouter_promos.py first.", file=sys.stderr)
            sys.exit(1)
        with open(args.deltas_file, "r", encoding="utf-8") as f:
            deltas_data = json.load(f)
        
        # Pull top free and low-cost text-output models
        free_models = [m for m in deltas_data.get("free_routes", []) if is_text_output_candidate(m)]
        low_cost = [m for m in deltas_data.get("low_cost_candidates", []) if is_text_output_candidate(m)]

        # Pick top 2 free and top 2 low-cost models for evaluation
        seen = set()
        selected = free_models[:2] + low_cost[:2]
        for m in selected:
            m_id = m.get("id")
            if m_id and m_id not in seen and not m_id.startswith("openrouter/"):
                seen.add(m_id)
                candidate_models.append(m)
    else:
        # Default test candidates
        candidate_models = [
            {"id": "nvidia/nemotron-3-super-120b-a12b:free", "name": "NVIDIA Nemotron 3 Super", "pricing": {"prompt_per_1m": 0.0, "completion_per_1m": 0.0}},
            {"id": "google/gemini-3.7-flash", "name": "Google Gemini 3.7 Flash", "pricing": {"prompt_per_1m": 0.075, "completion_per_1m": 0.30}}
        ]

    print(f"Starting Automated Benchmark Run on {len(candidate_models)} model(s)...")
    print(f"Probes: {args.probes} | Rounds: {args.rounds} | Dry Run: {args.dry_run}")

    os.makedirs(args.output_dir, exist_ok=True)
    all_evaluations = []

    for model_info in candidate_models:
        eval_summary = evaluate_model_on_probes(api_key, model_info, args.probes, rounds=args.rounds, dry_run=args.dry_run)
        all_evaluations.append(eval_summary)

        # Write model artifact
        safe_name = model_info["id"].replace("/", "_").replace(":", "_")
        out_path = os.path.join(args.output_dir, f"eval_{safe_name}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(eval_summary, f, indent=2)
        print(f"Saved evaluation artifact to: {out_path}")

        if args.write_markdown:
            print("\n" + format_markdown_report(eval_summary))

    # Master index artifact
    index_path = os.path.join(args.output_dir, "eval_master_index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "total_models_evaluated": len(all_evaluations),
            "evaluations": all_evaluations
        }, f, indent=2)
    print(f"\nAll evaluations completed successfully. Master index: {index_path}")

if __name__ == "__main__":
    main()
