#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
"""Validate the report registry's format and integrity.

Catches the drift that would make archive_reports.py silently no-op:
malformed rows, bad dates, link-text/target mismatch, missing report files,
duplicate entries, and unknown status values.

Usage:
    uv run --script validate_registry.py [--reports-dir .claude/reports] [--strict]

Exit code: 0 if no errors, 1 if any errors. With --strict, warnings also fail.
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

VALID_STATUSES = {"Active", "Completed", "Superseded", "Archived"}

# Canonical report row: | [name.md](category/name.md) | YYYY-MM-DD | Status | Summary |
ROW_RE = re.compile(r"\| \[(.*?)\]\((.*?)\) \| (.*?) \| (.*?) \| (.*?) \|\s*$")


def validate(reports_dir: Path) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for the registry under reports_dir."""
    errors: list[str] = []
    warnings: list[str] = []

    registry = reports_dir / "_registry.md"
    if not registry.exists():
        return [f"Registry not found: {registry}"], []

    seen: set[str] = set()
    referenced: set[str] = set()

    for lineno, line in enumerate(registry.read_text().splitlines(), start=1):
        # Only consider markdown-link table rows (report entries).
        if not line.lstrip().startswith("| ["):
            continue
        m = ROW_RE.match(line.strip())
        if not m:
            errors.append(f"L{lineno}: malformed report row: {line.strip()!r}")
            continue

        text, target, date, status, _summary = m.groups()

        if "/" not in target:
            errors.append(f"L{lineno}: target '{target}' missing category/ prefix")
            continue
        if Path(target).name != text:
            errors.append(f"L{lineno}: link text '{text}' != target file '{Path(target).name}'")

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            errors.append(f"L{lineno}: invalid date '{date}' (want ISO YYYY-MM-DD)")

        if status not in VALID_STATUSES:
            errors.append(f"L{lineno}: unknown status '{status}' (want one of {sorted(VALID_STATUSES)})")

        if target in seen:
            errors.append(f"L{lineno}: duplicate entry for '{target}'")
        seen.add(target)
        referenced.add(target)

        report_path = reports_dir / target
        if not report_path.exists():
            errors.append(f"L{lineno}: report file missing: {report_path}")

    # Orphan report files on disk that aren't registered (warning only).
    skip_dirs = {"archive"}
    for path in reports_dir.rglob("*.md"):
        rel = path.relative_to(reports_dir)
        if len(rel.parts) < 2 or rel.parts[0] in skip_dirs:
            continue  # top-level templates/registry, or archived files
        if str(rel) not in referenced:
            warnings.append(f"Unregistered report file on disk: {rel}")

    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the report registry")
    parser.add_argument("--reports-dir", default=".claude/reports")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args(argv)

    errors, warnings = validate(Path(args.reports_dir))

    for w in warnings:
        print(f"⚠️  {w}")
    for e in errors:
        print(f"❌ {e}")

    if not errors and not warnings:
        print("✅ Registry is valid.")
    else:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
