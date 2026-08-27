#!/usr/bin/env python3
"""
check_openrouter_promos.py

Fetches OpenRouter live model registry, parses pricing per 1M tokens,
identifies promotional discounts, free routes, and generational price drops,
and outputs a structured delta analysis artifact.
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error

OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"
ROUTING_MATRIX_PATH = os.path.expanduser("/Users/jason/model-ops/routing-matrix.md")
OUTPUT_PATH = os.path.expanduser("~/.hermes/telemetry/openrouter-model-deltas.json")

def fetch_openrouter_models():
    req = urllib.request.Request(
        OPENROUTER_MODELS_URL,
        headers={"User-Agent": "Hermes-Model-Ops/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("data", [])
    except Exception as e:
        print(f"Error fetching OpenRouter models: {e}", file=sys.stderr)
        return []

def parse_pricing(model):
    pricing = model.get("pricing", {})
    try:
        prompt_cost = float(pricing.get("prompt", 0)) * 1_000_000
    except (ValueError, TypeError):
        prompt_cost = 0.0

    try:
        completion_cost = float(pricing.get("completion", 0)) * 1_000_000
    except (ValueError, TypeError):
        completion_cost = 0.0

    return {
        "prompt_per_1m": round(prompt_cost, 4),
        "completion_per_1m": round(completion_cost, 4),
        "total_blended_1m": round((prompt_cost * 0.75) + (completion_cost * 0.25), 4),
        "is_free": prompt_cost == 0.0 and completion_cost == 0.0
    }

def is_text_output_model(model):
    architecture = model.get("architecture") or {}
    output_modalities = architecture.get("output_modalities") or []
    modality = architecture.get("modality") or ""

    if output_modalities:
        return set(output_modalities) == {"text"}

    return modality.endswith("->text")


def parse_routing_matrix():
    """
    Extracts known models and their reference/baseline pricing if documented in routing-matrix.md.
    """
    matrix_models = {}
    if not os.path.exists(ROUTING_MATRIX_PATH):
        return matrix_models

    try:
        with open(ROUTING_MATRIX_PATH, "r") as f:
            content = f.read()

        # Find all openrouter model mentions e.g. `openrouter/openai/gpt-5.6-luna`
        # and optional pricing annotations like ($0.20/$1.20) or ($0.090/$0.200/1M)
        lines = content.splitlines()
        for line in lines:
            matches = re.findall(r"`openrouter/([^`]+)`", line)
            # Check if there's pricing in this line: ($0.20/$1.20) or ($0.090/$0.200/1M) or ($0.075/1M)
            price_match = re.search(r"\(\$([0-9.]+)(?:/\$([0-9.]+))?(?:/1M)?\)", line)
            prompt_ref = None
            comp_ref = None
            if price_match:
                p1 = float(price_match.group(1))
                p2 = float(price_match.group(2)) if price_match.group(2) else p1
                prompt_ref = p1
                comp_ref = p2

            for m in matches:
                m_clean = m.strip()
                if m_clean not in matrix_models:
                    matrix_models[m_clean] = {
                        "in_routing_matrix": True,
                        "ref_prompt_1m": prompt_ref,
                        "ref_comp_1m": comp_ref,
                        "ref_blended_1m": round((prompt_ref * 0.75) + (comp_ref * 0.25), 4) if (prompt_ref is not None and comp_ref is not None) else None
                    }
    except Exception as e:
        print(f"Warning: Could not parse routing-matrix.md: {e}", file=sys.stderr)

    return matrix_models

def analyze_models(models):
    matrix_models = parse_routing_matrix()
    candidates = []
    free_models = []
    cost_drops = []
    
    for m in models:
        m_id = m.get("id", "")
        name = m.get("name", "")
        context_len = m.get("context_length", 0)
        pricing = parse_pricing(m)
        
        info = {
            "id": m_id,
            "name": name,
            "context_length": context_len,
            "pricing": pricing,
            "description": m.get("description", "")[:200],
            "architecture": m.get("architecture") or {},
            "supported_parameters": m.get("supported_parameters") or [],
            "text_output_only": is_text_output_model(m)
        }
        
        # Check against routing matrix for cost drops or promo detection
        # e.g., if model is free or discounted vs reference
        if m_id in matrix_models:
            ref = matrix_models[m_id]
            info["matrix_tracked"] = True
            if ref["ref_blended_1m"] is not None and ref["ref_blended_1m"] > 0:
                current_blended = pricing["total_blended_1m"]
                drop_pct = round(((ref["ref_blended_1m"] - current_blended) / ref["ref_blended_1m"]) * 100, 2)
                if drop_pct >= 20.0:
                    cost_drops.append({
                        "id": m_id,
                        "name": name,
                        "baseline_blended_1m": ref["ref_blended_1m"],
                        "current_blended_1m": current_blended,
                        "drop_percentage": drop_pct,
                        "is_promo": True
                    })
        
        if pricing["is_free"] and context_len >= 32768 and info["text_output_only"]:
            free_models.append(info)
        elif 0.0 <= pricing["total_blended_1m"] <= 1.50 and context_len >= 65536 and info["text_output_only"]:
            candidates.append(info)

    # Sort candidates by blended cost
    candidates.sort(key=lambda x: x["pricing"]["total_blended_1m"])
    free_models.sort(key=lambda x: x["context_length"], reverse=True)
    cost_drops.sort(key=lambda x: x["drop_percentage"], reverse=True)

    return {
        "total_models_scanned": len(models),
        "free_routes_count": len(free_models),
        "low_cost_candidates_count": len(candidates),
        "significant_cost_drops_count": len(cost_drops),
        "cost_drops_and_promos": cost_drops,
        "free_routes": free_models[:15],
        "low_cost_candidates": candidates[:30]
    }

def main():
    print("Fetching OpenRouter catalog...")
    models = fetch_openrouter_models()
    if not models:
        print("Failed to retrieve model registry.", file=sys.stderr)
        sys.exit(1)

    print(f"Retrieved {len(models)} models from OpenRouter. Analyzing pricing and deltas...")
    analysis = analyze_models(models)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"Wrote OpenRouter delta analysis to: {OUTPUT_PATH}")
    print(f"Summary: {analysis['free_routes_count']} free routes (>=32k ctx), {analysis['low_cost_candidates_count']} low-cost candidates (<= $1.50/1M blended), {analysis['significant_cost_drops_count']} >=20% cost drops/promos.")

if __name__ == "__main__":
    main()
