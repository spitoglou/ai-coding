#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Append a report entry to the registry (and optionally scaffold the file).

Keeps registry rows in the one canonical format the rest of the tooling
(archive_reports.py, validate_registry.py) expects:

    | [name.md](category/name.md) | YYYY-MM-DD | Status | Summary |

The row is inserted under the matching `### Category` heading inside the
`## All Reports by Category` section, creating the table scaffolding if needed.

`--name` is the report stem WITHOUT the date (matching verify.py); the date is
appended to form `{name}-{date}.md`.

Usage:
    uv run --script add_report.py --category review --name review-src \\
        --status Completed --summary "Peer review of src/" [--date 2026-07-24] \\
        [--scaffold] [--reports-dir .claude/reports]
"""

import argparse
import sys
from datetime import date as date_cls
from pathlib import Path

VALID_STATUSES = ("Active", "Completed", "Superseded", "Archived")
BY_CATEGORY_HEADING = "## All Reports by Category"
TABLE_HEADER = "| Report | Date | Status | Summary |\n"
TABLE_SEPARATOR = "|--------|------|--------|---------|\n"


def normalize_name(name: str) -> str:
    """Return the report basename with a single .md extension."""
    return name[:-3] if name.endswith(".md") else name


def build_row(category: str, filename: str, date: str, status: str, summary: str) -> str:
    """Build one canonical registry table row."""
    return f"| [{filename}]({category}/{filename}) | {date} | {status} | {summary} |\n"


def find_category_index(lines: list[str], category: str) -> int | None:
    """Index of the `### {category}` heading within the by-category section.

    Case-insensitive on the category name. Returns None if not found.
    """
    in_section = False
    for i, line in enumerate(lines):
        if line.startswith(BY_CATEGORY_HEADING):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break  # left the by-category section
        if in_section and line.startswith("### "):
            heading = line[4:].strip().lower()
            if heading == category.lower():
                return i
    return None


def insert_row(lines: list[str], cat_idx: int, row: str) -> list[str]:
    """Insert `row` under the category heading at cat_idx, scaffolding a table.

    Places the row after any existing rows in the category's table; creates the
    table header/separator if the section has none yet.
    """
    # Scan the category body until the next heading.
    end = len(lines)
    for j in range(cat_idx + 1, len(lines)):
        if lines[j].startswith(("### ", "## ")):
            end = j
            break

    body = range(cat_idx + 1, end)
    header_idx = next((j for j in body if lines[j].startswith("| Report |")), None)

    if header_idx is not None:
        # Find the last data row after the separator; insert after it.
        insert_at = header_idx + 2  # skip header + separator
        j = insert_at
        while j < end and lines[j].startswith("|"):
            j += 1
        lines.insert(j, row)
        return lines

    # No table yet: insert header + separator + row after leading comments/blanks.
    insert_at = cat_idx + 1
    while insert_at < end and (
        lines[insert_at].strip() == "" or lines[insert_at].lstrip().startswith("<!--")
    ):
        insert_at += 1
    scaffold = [TABLE_HEADER, TABLE_SEPARATOR, row]
    lines[insert_at:insert_at] = scaffold
    return lines


def update_last_updated(lines: list[str], today: str) -> list[str]:
    """Refresh the `**Last Updated:**` line if present."""
    for i, line in enumerate(lines):
        if line.startswith("**Last Updated:**"):
            lines[i] = f"**Last Updated:** {today}\n"
            break
    return lines


def scaffold_report(path: Path, name: str, date: str, status: str, summary: str) -> None:
    """Create a minimal report file if it does not already exist."""
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# {name}\n\n"
        f"**Date:** {date}  \n"
        f"**Status:** {status}\n\n"
        f"## Summary\n\n{summary}\n\n"
        f"## Findings\n\n_TODO_\n\n"
        f"## Recommendations\n\n_TODO_\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Append a report entry to the registry")
    parser.add_argument("--category", required=True, help="Report category (e.g. review)")
    parser.add_argument("--name", required=True, help="Report stem WITHOUT date (e.g. review-src)")
    parser.add_argument("--summary", required=True, help="One-line summary")
    parser.add_argument("--status", default="Completed", choices=VALID_STATUSES)
    parser.add_argument("--date", default=None, help="ISO date (default: today)")
    parser.add_argument("--reports-dir", default=".claude/reports")
    parser.add_argument("--scaffold", action="store_true", help="Create the report file if missing")
    args = parser.parse_args(argv)

    today = args.date or date_cls.today().isoformat()
    category = args.category.lower()
    # `--name` is the stem WITHOUT the date, matching verify.py's contract;
    # the date is appended to form the filename: {name}-{date}.md
    stem = normalize_name(args.name)
    filename = f"{stem}-{today}.md"

    reports_dir = Path(args.reports_dir)
    registry = reports_dir / "_registry.md"
    if not registry.exists():
        print(f"❌ Registry not found: {registry} (run bootstrap.py first)", file=sys.stderr)
        return 1

    lines = registry.read_text().splitlines(keepends=True)
    if not any(line.startswith(BY_CATEGORY_HEADING) for line in lines):
        print(f"❌ Registry missing '{BY_CATEGORY_HEADING}' section", file=sys.stderr)
        return 1

    cat_idx = find_category_index(lines, category)
    if cat_idx is None:
        # Append a new category section at the end of the by-category block.
        end = len(lines)
        in_section = False
        for i, line in enumerate(lines):
            if line.startswith(BY_CATEGORY_HEADING):
                in_section = True
                continue
            if in_section and line.startswith("## "):
                end = i
                break
        new_section = [f"### {category.title()}\n", "\n"]
        lines[end:end] = new_section
        cat_idx = end

    row = build_row(category, filename, today, args.status, args.summary)
    lines = insert_row(lines, cat_idx, row)
    lines = update_last_updated(lines, today)
    registry.write_text("".join(lines))

    if args.scaffold:
        title = filename[:-3]  # basename without .md
        scaffold_report(reports_dir / category / filename, title, today, args.status, args.summary)

    print(f"✅ Added registry entry: {category}/{filename} ({today}, {args.status})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
