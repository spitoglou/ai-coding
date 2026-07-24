"""Tests for archive_reports.py and verify.py."""

import subprocess
import sys
from pathlib import Path

from conftest import run_script


def add_dated_report(project: Path, category: str, name: str, date: str) -> None:
    """Add a report; final filename is {name}-{date}.md."""
    run_script(
        project, "add_report.py",
        "--category", category, "--name", name,
        "--summary", "s", "--scaffold", "--date", date,
    )


def test_archive_moves_old_report(project: Path):
    add_dated_report(project, "review", "old", "2000-01-01")
    r = run_script(project, "archive_reports.py", "7")
    assert r.returncode == 0, r.stderr
    # File moved out of active category into archive/.
    assert not (project / ".claude/reports/review/old-2000-01-01.md").exists()
    assert (project / ".claude/reports/archive/review/old-2000-01-01.md").exists()
    # Removed from active registry.
    reg = (project / ".claude/reports/_registry.md").read_text()
    assert "old-2000-01-01.md](review/old-2000-01-01.md)" not in reg


def test_archive_keeps_recent_report(project: Path):
    add_dated_report(project, "review", "fresh", "2026-07-24")
    run_script(project, "archive_reports.py", "7")
    assert (project / ".claude/reports/review/fresh-2026-07-24.md").exists()


def test_archive_dry_run_moves_nothing(project: Path):
    add_dated_report(project, "review", "old", "2000-01-01")
    run_script(project, "archive_reports.py", "7", "--dry-run")
    assert (project / ".claude/reports/review/old-2000-01-01.md").exists()


def _verify(project: Path, *args: str):
    return subprocess.run(
        [sys.executable, ".claude/skills/agent-coordination/scripts/verify.py", *args],
        cwd=project, capture_output=True, text=True,
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
