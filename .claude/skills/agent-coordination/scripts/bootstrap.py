#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
"""Bootstrap the agent-coordination runtime state in a project.

Cross-platform replacement for bootstrap.sh. Idempotent: safe to run
repeatedly. Seeds the report registries from their templates (without
overwriting existing ones), creates the report category directories the
commands expect, runs the deterministic project adaptation (adapt.py), and
lints agent/command frontmatter so a malformed definition is reported at
install time rather than silently failing to load mid-task.

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

SCRIPTS = ".claude/skills/agent-coordination/scripts"
ADAPT = f"{SCRIPTS}/adapt.py"
VALIDATE_FRONTMATTER = f"{SCRIPTS}/validate_frontmatter.py"


def seed_from_template(template: Path, target: Path, today: str) -> None:
    """Seed target from template (with date filled in) unless it already exists."""
    if target.exists():
        print(f"• Exists, leaving as-is: {target}")
    elif template.exists():
        target.write_text(
            template.read_text(encoding="utf-8").replace("YYYY-MM-DD", today),
            encoding="utf-8",
        )
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

    # Lint agent/command frontmatter. A block that fails to parse means the
    # agent is missing from the registry (or the command loses its description)
    # with no error until something tries to use it, so surface it here.
    # Non-fatal: one bad definition must not block the rest of setup.
    if Path(VALIDATE_FRONTMATTER).exists():
        result = subprocess.run(["uv", "run", "--script", VALIDATE_FRONTMATTER])
        if result.returncode != 0:
            print(
                "⚠️  The definitions above will NOT load correctly. Fix their "
                "frontmatter, then restart the session.",
                file=sys.stderr,
            )

    print("Bootstrap complete.")
    return 0


if __name__ == "__main__":
    # Windows defaults piped stdout/stderr to a legacy codepage (cp1252), which
    # makes the status glyphs above raise UnicodeEncodeError. Force UTF-8.
    # line_buffering keeps our output ordered against the child scripts' when
    # piped; block buffering would flush all of ours after theirs.
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)
    raise SystemExit(main())
