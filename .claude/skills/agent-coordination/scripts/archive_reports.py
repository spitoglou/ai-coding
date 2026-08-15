#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
"""Archive old registry entries and reports.

Moves registry entries and their associated report files older than N days
to the archive directory while preserving structure and maintaining history.

Registry rows are the one canonical format shared with add_report.py and
validate_registry.py:

    | [name.md](category/name.md) | YYYY-MM-DD | Status | Summary |

Any other shape is reported as an unparsed entry rather than silently skipped,
because a parser that matches nothing used to print "Archived: 0 / Remaining: 0"
and read as "nothing to do".
"""

import re
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Canonical report row: | [name.md](category/name.md) | YYYY-MM-DD | Status | Summary |
ROW_RE = re.compile(r"\| \[(.*?)\]\((.*?)\) \| (\d{4}-\d{2}-\d{2}) \| (.*?) \| (.*?) \|\s*$")

# Anything that *looks* like a registry entry, canonical or not. Used only to
# tell "the registry is empty" apart from "the parser understood none of it".
CANDIDATE_RE = re.compile(r"^\s*(?:\|\s*\[|-\s*\[|-\s+\S+\s*\|)")

TABLE_HEADER = "| Report | Date | Status | Summary |\n"
TABLE_SEPARATOR = "|--------|------|--------|---------|\n"


def parse_date(date_str: str) -> datetime:
    """Parse date from registry entry (YYYY-MM-DD format)."""
    return datetime.strptime(date_str, "%Y-%m-%d")


def is_older_than(date_str: str, days_threshold: int) -> bool:
    """Check if date is older than threshold days."""
    entry_date = parse_date(date_str)
    threshold_date = datetime.now() - timedelta(days=days_threshold)
    return entry_date < threshold_date


def extract_report_info(
    line: str,
) -> tuple[str | None, str | None, str | None, str | None, str | None]:
    """Extract (filename, date, status, category, target) from a registry line.

    `target` is the link destination relative to the reports dir, e.g.
    "review/review-src-2026-01-13.md" — it is what locates the file on disk;
    `category` is its first path segment.

    Returns a 5-tuple of None if the line is not a canonical report row.
    """
    match = ROW_RE.match(line.strip())
    if not match:
        return None, None, None, None, None

    filename, target, date, status, _summary = match.groups()

    # A target without a category segment cannot be placed in the archive tree.
    category = target.split("/")[0] if "/" in target else None

    return filename, date, status, category, target


def build_row(target: str, date: str, status: str, summary: str) -> str:
    """Build one canonical registry row from its parts."""
    return f"| [{Path(target).name}]({target}) | {date} | {status} | {summary} |\n"


def read_existing_archive(archive_registry: Path) -> dict[str, tuple[str, str, str]]:
    """Read an existing dated archive registry into {target: (date, status, summary)}.

    Archive registries are re-read rather than overwritten so that a second run
    on the same day merges into the first run's batch instead of truncating it.
    """
    existing: dict[str, tuple[str, str, str]] = {}
    if not archive_registry.exists():
        return existing

    for line in archive_registry.read_text(encoding="utf-8").splitlines():
        match = ROW_RE.match(line.strip())
        if not match:
            continue
        _filename, target, date, status, summary = match.groups()
        existing[target] = (date, status, summary)
    return existing


def write_archive_registry(
    archive_registry: Path,
    rows: dict[str, tuple[str, str, str]],
    days_threshold: int,
    merged_count: int,
) -> None:
    """Write the dated archive registry, grouped by category."""
    by_category: dict[str, list[str]] = {}
    for target, (date, _status, summary) in sorted(rows.items()):
        category = target.split("/")[0]
        # Status is normalised to "Archived" — that is what being in this file means.
        by_category.setdefault(category, []).append(
            build_row(target, date, "Archived", summary)
        )

    with open(archive_registry, "w", encoding="utf-8") as f:
        f.write("# Archived Reports\n\n")
        f.write(f"**Archive Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"**Threshold:** Reports older than {days_threshold} days\n")
        f.write(f"**Total Archived:** {len(rows)} reports\n")
        if merged_count:
            f.write(f"**Merged from earlier run(s) today:** {merged_count} reports\n")
        f.write("\n---\n\n")

        for category, entries in sorted(by_category.items()):
            f.write(f"### {category.title()}\n\n")
            f.write(TABLE_HEADER)
            f.write(TABLE_SEPARATOR)
            for entry in entries:
                f.write(entry)
            f.write("\n---\n\n")


def archive_reports(days_threshold: int = 7, dry_run: bool = False) -> int:
    """Archive reports older than days_threshold.

    Args:
        days_threshold: Archive entries older than this many days
        dry_run: If True, only print what would be archived without moving files

    Returns:
        0 on success, 1 if the registry could not be parsed.
    """
    reports_dir = Path(".claude/reports")
    registry_file = reports_dir / "_registry.md"
    archive_dir = reports_dir / "archive"

    # Dated archive registry (e.g. _registry-archive-2025-12-28.md). A second
    # run on the same day merges into this file rather than replacing it.
    archive_date = datetime.now().strftime("%Y-%m-%d")
    archive_registry = archive_dir / f"_registry-archive-{archive_date}.md"

    if not registry_file.exists():
        print(f"❌ Registry not found: {registry_file}")
        return 1

    if not dry_run:
        archive_dir.mkdir(exist_ok=True)

    with open(registry_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    archived_entries: list[tuple[str, str, str, str]] = []  # target, date, status, summary
    remaining_entries: list[str] = []
    candidate_lines = 0
    parsed_lines = 0

    in_fence = False

    for line in lines:
        # The registry documents its own row format in a fenced example. Skip
        # fenced blocks so that example is neither archived nor counted.
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            remaining_entries.append(line)
            continue
        if in_fence:
            remaining_entries.append(line)
            continue

        if CANDIDATE_RE.match(line):
            candidate_lines += 1

        filename, date, status, category, target = extract_report_info(line)

        if not (filename and date and category and target):
            # Headers, separators, comments, prose — and malformed rows, which
            # the candidate counter above accounts for.
            remaining_entries.append(line)
            continue

        parsed_lines += 1

        if not is_older_than(date, days_threshold):
            remaining_entries.append(line)
            continue

        summary = ROW_RE.match(line.strip()).group(5)
        archived_entries.append((target, date, status, summary))
        print(f"📦 Archiving: {target} (Date: {date}, Status: {status})")

        source_file = reports_dir / target
        dest_file = archive_dir / target
        if source_file.exists():
            if not dry_run:
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source_file), str(dest_file))
                print(f"  ✅ Moved: {source_file} → {dest_file}")
            else:
                print(f"  [DRY RUN] Would move: {source_file} → {dest_file}")
        else:
            print(f"  ⚠️  File not found: {source_file}")

    # A registry full of entries that the parser understood none of is a format
    # drift, not an empty registry. Say so loudly instead of reporting 0/0.
    if candidate_lines and not parsed_lines:
        print(
            f"\n❌ Parsed 0 of {candidate_lines} entry-like line(s) in {registry_file}.\n"
            f"   Rows must be: | [name.md](category/name.md) | YYYY-MM-DD | Status | Summary |\n"
            f"   Run validate_registry.py for a line-by-line diagnosis."
        )
        return 1
    if candidate_lines > parsed_lines:
        print(
            f"\n⚠️  {candidate_lines - parsed_lines} entry-like line(s) were not in the "
            f"canonical row format and were left untouched. Run validate_registry.py."
        )

    if not dry_run:
        with open(registry_file, "w", encoding="utf-8") as f:
            f.writelines(remaining_entries)
        print(f"\n✅ Updated active registry: {registry_file}")
    else:
        print(f"\n[DRY RUN] Would update: {registry_file}")

    merged_count = 0
    if archived_entries:
        existing = read_existing_archive(archive_registry)
        merged_count = len(existing)
        combined = dict(existing)
        for target, date, _status, summary in archived_entries:
            combined[target] = (date, "Archived", summary)

        if not dry_run:
            write_archive_registry(
                archive_registry, combined, days_threshold, merged_count
            )
            if merged_count:
                print(
                    f"✅ Merged into existing archive registry "
                    f"({merged_count} prior + {len(archived_entries)} new): {archive_registry}"
                )
            else:
                print(f"✅ Created dated archive registry: {archive_registry}")
        else:
            action = "merge into" if merged_count else "create"
            print(f"[DRY RUN] Would {action}: {archive_registry}")

    print("\n📊 Summary:")
    print(f"  - Archive Date: {archive_date}")
    print(f"  - Threshold: {days_threshold} days")
    print(f"  - Entry lines seen: {candidate_lines} ({parsed_lines} parsed)")
    print(f"  - Archived: {len(archived_entries)} reports")
    print(f"  - Remaining: {parsed_lines - len(archived_entries)} reports")
    if archived_entries:
        print(f"  - Registry: {archive_registry.name}")
        if merged_count:
            print(f"  - Merged with earlier run today: {merged_count} prior reports")

    if dry_run:
        print("\n⚠️  DRY RUN - No files were actually moved")

    return 0


if __name__ == "__main__":
    import argparse

    # Windows defaults piped stdout/stderr to a legacy codepage (cp1252), which
    # makes the status glyphs above raise UnicodeEncodeError. Force UTF-8.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Archive old registry entries")
    parser.add_argument(
        "days",
        type=int,
        nargs="?",
        default=7,
        help="Archive entries older than N days (default: 7)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be archived without moving files"
    )

    args = parser.parse_args()

    print(f"🗄️  Archive Reports")
    print(f"{'=' * 60}\n")

    raise SystemExit(archive_reports(days_threshold=args.days, dry_run=args.dry_run))
