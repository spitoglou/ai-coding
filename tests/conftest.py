"""Shared fixtures for toolkit script tests.

Tests invoke the scripts as shipped (via subprocess) inside a throwaway copy of
the toolkit, so they exercise real argparse/exit-code behavior and the bash
scripts too.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_SRC = REPO_ROOT / ".claude"
SCRIPTS_REL = ".claude/skills/agent-coordination/scripts"


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """A bootstrapped project copy: tmp_path/.claude with seeded registries.

    Runtime report state is deliberately NOT copied. `.claude/reports/` is
    gitignored working state, so carrying it in would let whatever reports the
    developer happens to have locally change what the tests see — entry counts,
    archive batches and parse totals all shift under them. Only the templates
    come across; bootstrap.py seeds the registries fresh from those.
    """
    shutil.copytree(CLAUDE_SRC, tmp_path / ".claude")

    reports = tmp_path / ".claude/reports"
    if reports.exists():
        templates = [p for p in reports.iterdir() if p.is_file() and p.name.endswith("-template.md")]
        kept = {p.name: p.read_bytes() for p in templates}
        shutil.rmtree(reports)
        reports.mkdir(parents=True)
        for name, data in kept.items():
            (reports / name).write_bytes(data)

    subprocess.run(
        ["uv", "run", "--script", f"{SCRIPTS_REL}/bootstrap.py"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return tmp_path


def run_script(project_dir: Path, script: str, *args: str) -> subprocess.CompletedProcess:
    """Run a python toolkit script with the project dir as cwd."""
    return subprocess.run(
        ["uv", "run", "--script", f"{SCRIPTS_REL}/{script}", *args],
        cwd=project_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
