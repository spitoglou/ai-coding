"""Tests for add_report.py and validate_registry.py."""

from pathlib import Path

from conftest import run_script


def registry(project: Path) -> str:
    return (project / ".claude/reports/_registry.md").read_text(encoding="utf-8")


def test_add_report_writes_canonical_row(project: Path):
    r = run_script(
        project, "add_report.py",
        "--category", "review", "--name", "review-src",
        "--summary", "Peer review", "--date", "2026-07-24",
    )
    assert r.returncode == 0, r.stderr
    assert (
        "| [review-src-2026-07-24.md](review/review-src-2026-07-24.md) "
        "| 2026-07-24 | Completed | Peer review |"
    ) in registry(project)


def test_add_report_strips_double_extension(project: Path):
    run_script(
        project, "add_report.py",
        "--category", "bugs", "--name", "bugs-x",
        "--summary", "s", "--date", "2026-07-24",
    )
    # No ".md.md" should appear.
    assert ".md.md" not in registry(project)
    assert "bugs-x-2026-07-24.md](bugs/bugs-x-2026-07-24.md)" in registry(project)


def test_add_report_scaffold_creates_file(project: Path):
    run_script(
        project, "add_report.py",
        "--category", "review", "--name", "r",
        "--summary", "s", "--scaffold", "--date", "2026-07-24",
    )
    assert (project / ".claude/reports/review/r-2026-07-24.md").exists()


def test_add_report_updates_last_updated(project: Path):
    run_script(
        project, "add_report.py",
        "--category", "review", "--name", "r",
        "--summary", "s", "--date", "2026-07-24",
    )
    assert "**Last Updated:** 2026-07-24" in registry(project)


def test_validate_passes_for_scaffolded_entry(project: Path):
    run_script(
        project, "add_report.py",
        "--category", "security", "--name", "security-scan",
        "--summary", "s", "--scaffold", "--date", "2026-07-24",
    )
    v = run_script(project, "validate_registry.py")
    assert v.returncode == 0, v.stdout + v.stderr
    # A registered report must not also be reported as an orphan on disk. This
    # regressed on Windows, where the on-disk relative path uses backslashes
    # and never matched the registry's forward-slash targets.
    assert "security-scan-2026-07-24.md" not in v.stdout


def test_validate_flags_missing_file(project: Path):
    # Add an entry WITHOUT scaffolding the file.
    run_script(
        project, "add_report.py",
        "--category", "review", "--name", "ghost",
        "--summary", "s", "--date", "2026-07-24",
    )
    v = run_script(project, "validate_registry.py")
    assert v.returncode == 1
    assert "report file missing" in v.stdout


def test_validate_flags_bullet_entries(project: Path):
    """A bullet-format registry must fail, not validate clean.

    The pre-0.3 validator only inspected lines starting with "| [", so a
    registry written entirely in the legacy bullet form passed with 0 errors
    while archive_reports.py could parse none of it. That blind spot is why the
    broken archiver went unnoticed.
    """
    reg = project / ".claude/reports/_registry.md"
    reg.write_text(
        reg.read_text(encoding="utf-8")
        + "\n### Review\n"
        + "- infrastructure-assessment-20260113 | Active | Consolidated assessment\n"
        + "- [linked-form-20260113](review/linked-form-20260113.md) | Completed | Linked bullet\n",
        encoding="utf-8",
    )
    v = run_script(project, "validate_registry.py")
    assert v.returncode == 1
    assert v.stdout.count("non-canonical bullet entry") == 2


def test_validate_ignores_fenced_examples(project: Path):
    """The registry documents its own row format in a fenced block.

    That example must not be validated as a real entry, or every registry
    seeded from the template starts out failing.
    """
    v = run_script(project, "validate_registry.py")
    assert v.returncode == 0, v.stdout
    assert "category/name.md" not in v.stdout


def test_validate_flags_bad_date_and_status(project: Path):
    reg = project / ".claude/reports/_registry.md"
    lines = reg.read_text(encoding="utf-8").splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("### Review"):
            lines[i + 1:i + 1] = [
                "| Report | Date | Status | Summary |\n",
                "|--------|------|--------|---------|\n",
                "| [b.md](review/b.md) | 07-24-2026 | Weird | bad |\n",
            ]
            break
    reg.write_text("".join(lines), encoding="utf-8")
    v = run_script(project, "validate_registry.py")
    assert v.returncode == 1
    assert "invalid date" in v.stdout
    assert "unknown status" in v.stdout
