"""Tests for bootstrap.py and install.py (idempotency + non-destructiveness)."""

import subprocess
from pathlib import Path

from conftest import REPO_ROOT, SCRIPTS_REL


def test_bootstrap_seeds_registries(project: Path):
    assert (project / ".claude/reports/_registry.md").exists()
    assert (project / ".claude/reports/_tech-debt.md").exists()
    # Category dirs created.
    for cat in ("review", "security", "sre", "archive"):
        assert (project / ".claude/reports" / cat).is_dir()


def test_bootstrap_is_non_destructive(project: Path):
    reg = project / ".claude/reports/_registry.md"
    reg.write_text(reg.read_text() + "\nSENTINEL_LOCAL\n")
    subprocess.run(
        ["uv", "run", "--script", f"{SCRIPTS_REL}/bootstrap.py"],
        cwd=project, check=True, capture_output=True, text=True,
    )
    assert "SENTINEL_LOCAL" in reg.read_text()


def test_install_preserves_local_reports(tmp_path: Path):
    target = tmp_path / "app"
    (target / ".claude").mkdir(parents=True)

    def install():
        return subprocess.run(
            ["uv", "run", "--script", "install.py", str(target)],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )

    r1 = install()
    assert r1.returncode == 0, r1.stderr

    reg = target / ".claude/reports/_registry.md"
    assert reg.exists()
    reg.write_text(reg.read_text() + "\nSENTINEL_LOCAL\n")
    local_report = target / ".claude/reports/review/local-2026-07-24.md"
    local_report.parent.mkdir(parents=True, exist_ok=True)
    local_report.write_text("local report body\n")

    # Simulate a project adaptation before updating.
    profile = target / ".claude/project.md"
    assert profile.exists()  # bootstrap/adapt generated it on first install
    profile.write_text(profile.read_text() + "\nADAPTATION_KEEPME\n")

    r2 = install()
    assert r2.returncode == 0, r2.stderr
    assert "SENTINEL_LOCAL" in reg.read_text()
    assert local_report.exists()
    assert (target / ".claude/VERSION").exists()
    # Project adaptation survives a core update.
    assert "ADAPTATION_KEEPME" in profile.read_text()
    # Shared config ships; session-local permissions never leak into targets.
    assert (target / ".claude/settings.json").exists()
    assert (target / ".claude/hooks/session_start.py").exists()
    assert not (target / ".claude/settings.local.json").exists()
    # The core ships the template, not the source project's own project.md.
    assert (target / ".claude/project-template.md").exists()


def test_install_check_is_read_only(tmp_path: Path):
    target = tmp_path / "app"
    (target / ".claude").mkdir(parents=True)
    subprocess.run(["uv", "run", "--script", "install.py", str(target)],
                   cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    before = (target / ".claude/project.md").read_text()
    r = subprocess.run(["uv", "run", "--script", "install.py", "--check", str(target)],
                       cwd=REPO_ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    # Up-to-date core reports no changes and touches nothing.
    assert "up to date" in r.stdout
    assert (target / ".claude/project.md").read_text() == before
