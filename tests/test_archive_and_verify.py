"""Tests for archive_reports.py and verify.py."""

import subprocess
from datetime import date, timedelta
from pathlib import Path

from conftest import run_script


def days_ago(n: int) -> str:
    """ISO date n days before today.

    Dates here are relative on purpose: a hardcoded "recent" date silently
    becomes an "old" one once the calendar passes it, turning a real assertion
    into a failure unrelated to any code change.
    """
    return (date.today() - timedelta(days=n)).isoformat()


def add_dated_report(project: Path, category: str, name: str, date_str: str) -> None:
    """Add a report; final filename is {name}-{date_str}.md."""
    run_script(
        project, "add_report.py",
        "--category", category, "--name", name,
        "--summary", "s", "--scaffold", "--date", date_str,
    )


def test_archive_moves_old_report(project: Path):
    add_dated_report(project, "review", "old", "2000-01-01")
    r = run_script(project, "archive_reports.py", "7")
    assert r.returncode == 0, r.stderr
    # File moved out of active category into archive/.
    assert not (project / ".claude/reports/review/old-2000-01-01.md").exists()
    assert (project / ".claude/reports/archive/review/old-2000-01-01.md").exists()
    # Removed from active registry.
    reg = (project / ".claude/reports/_registry.md").read_text(encoding="utf-8")
    assert "old-2000-01-01.md](review/old-2000-01-01.md)" not in reg


def test_archive_keeps_recent_report(project: Path):
    recent = days_ago(2)
    add_dated_report(project, "review", "fresh", recent)
    run_script(project, "archive_reports.py", "7")
    assert (project / f".claude/reports/review/fresh-{recent}.md").exists()


def test_archive_refuses_noncanonical_registry(project: Path):
    """A registry the parser cannot read must fail loudly, not report 0/0.

    Before 0.3 this printed "Archived: 0, Remaining: 0" and exited 0, which
    read as "nothing to do" rather than "no line was understood" — the reason
    the broken archiver survived so long.
    """
    reg = project / ".claude/reports/_registry.md"
    reg.write_text(
        reg.read_text(encoding="utf-8")
        + "\n### Review\n"
        + "- old-report-20000101 | Completed | Legacy bullet entry\n",
        encoding="utf-8",
    )
    r = run_script(project, "archive_reports.py", "7")
    assert r.returncode == 1, r.stdout
    assert "Parsed 0 of" in r.stdout


def test_archive_same_day_second_run_merges(project: Path):
    """A same-day re-run must not truncate the earlier batch.

    The archive registry filename is derived from today's date, so a second run
    reopened the same path; with 'w' it discarded the first run's rows, leaving
    those reports on disk under archive/ with no row in any registry.
    """
    add_dated_report(project, "review", "first", "2000-01-01")
    add_dated_report(project, "analysis", "second", days_ago(20))

    r1 = run_script(project, "archive_reports.py", "60")
    assert r1.returncode == 0, r1.stdout
    r2 = run_script(project, "archive_reports.py", "7")
    assert r2.returncode == 0, r2.stdout

    archives = list((project / ".claude/reports/archive").glob("_registry-archive-*.md"))
    assert len(archives) == 1, archives
    text = archives[0].read_text(encoding="utf-8")
    assert "first-2000-01-01.md" in text, "first run's batch was truncated"
    assert "second-" in text
    # Both files really moved, and both are recorded as Archived.
    assert (project / ".claude/reports/archive/review/first-2000-01-01.md").exists()
    assert text.count("| Archived |") == 2


def test_archive_dry_run_moves_nothing(project: Path):
    add_dated_report(project, "review", "old", "2000-01-01")
    run_script(project, "archive_reports.py", "7", "--dry-run")
    assert (project / ".claude/reports/review/old-2000-01-01.md").exists()


def _verify(project: Path, *args: str):
    return subprocess.run(
        ["uv", "run", "--script", ".claude/skills/agent-coordination/scripts/verify.py", *args],
        cwd=project, capture_output=True, text=True, encoding="utf-8",
    )


def test_verify_runs_all_checks(project: Path):
    add_dated_report(project, "review", "v", "2026-07-24")
    r = _verify(project, "review", "v", "2026-07-24")
    assert r.stdout.count("Report file exists") == 1
    assert "Report has content" in r.stdout
    assert "Registry entry exists" in r.stdout


def test_verify_passes_for_valid_deliverable(project: Path):
    add_dated_report(project, "review", "v", "2026-07-24")
    r = _verify(project, "review", "v", "2026-07-24")
    assert r.returncode == 0, r.stdout
    assert "3 passed" in r.stdout
