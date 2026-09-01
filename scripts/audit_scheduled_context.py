#!/usr/bin/env python3
"""Report scheduled-job prompt and loaded-skill context sizes.

Read-only audit: deliberately avoids credential files and execution history bodies.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=Path, required=True, dest="jobs_file")
    parser.add_argument("--skills-root", type=Path, required=True)
    parser.add_argument("--job", action="append", dest="job_names")
    args = parser.parse_args()

    payload = json.loads(args.jobs_file.read_text(encoding="utf-8"))
    jobs = payload.get("jobs", payload) if isinstance(payload, dict) else payload
    wanted = set(args.job_names or [])
    report = []
    for job in jobs:
        name = job.get("name")
        if wanted and name not in wanted:
            continue
        skill_sizes = {}
        for skill in job.get("skills") or []:
            matches = list(args.skills_root.rglob(f"{skill}/SKILL.md"))
            if matches:
                skill_sizes[skill] = matches[0].stat().st_size
        report.append({
            "name": name,
            "model": job.get("model"),
            "prompt_chars": len(job.get("prompt") or ""),
            "prompt_words": len((job.get("prompt") or "").split()),
            "loaded_skill_bytes": sum(skill_sizes.values()),
            "skill_sizes": skill_sizes,
        })
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
