#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
"""Bootstrap the agent-coordination runtime state in a project.

Cross-platform replacement for bootstrap.sh. Idempotent: safe to run
repeatedly. Seeds the report registries from their templates (without
overwriting existing ones), creates the report category directories the
commands expect, and runs the deterministic project adaptation (adapt.py).

Usage: run from the project root (the directory that contains .claude/)
    uv run --script bootstrap.py
"""

import subprocess
import sys
from datetime import date as date_cls
from pathlib import Path

CATEGORIES = [
    "analysis", "architecture", "bugs", "commits", "design", "exec", "handoffs",
    "implementation", "review", "tests", "security", "sre", "rfc", "ci", "archive",
]

ADAPT = ".claude/skills/agent-coordination/scripts/adapt.py"


def seed_from_template(template: Path, target: Path, today: str) -> None:
    """Seed target from template (with date filled in) unless it already exists."""
    if target.exists():
        print(f"• Exists, leaving as-is: {target}")
    elif template.exists():
        target.write_text(template.read_text().replace("YYYY-MM-DD", today))
        print(f"✅ Seeded: {target}")
    else:
        print(f"⚠️  Template missing, skipped: {template}", file=sys.stderr)


def main() -> int:
    if not Path(".claude").is_dir():
        print("❌ No .claude/ directory here. Run from the project root.", file=sys.stderr)
        return 1

    reports = Path(".claude/reports")
    reports.mkdir(parents=True, exist_ok=True)
    today = date_cls.today().isoformat()

    seed_from_template(reports / "_registry-template.md", reports / "_registry.md", today)
    seed_from_template(reports / "_tech-debt-template.md", reports / "_tech-debt.md", today)

    for category in CATEGORIES:
        (reports / category).mkdir(exist_ok=True)
    print(f"✅ Ensured {len(CATEGORIES)} report category directories")

    # Adapt the generic core to this project. Non-fatal: never block bootstrap.
    if Path(ADAPT).exists():
        result = subprocess.run(["uv", "run", "--script", ADAPT])
        if result.returncode != 0:
            print("⚠️  adapt.py failed, skipped", file=sys.stderr)

    print("Bootstrap complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
