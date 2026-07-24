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
    """A bootstrapped project copy: tmp_path/.claude with seeded registries."""
    shutil.copytree(CLAUDE_SRC, tmp_path / ".claude")
    subprocess.run(
        ["uv", "run", "--script", f"{SCRIPTS_REL}/bootstrap.py"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    return tmp_path


def run_script(project_dir: Path, script: str, *args: str) -> subprocess.CompletedProcess:
    """Run a python toolkit script with the project dir as cwd."""
    return subprocess.run(
        ["uv", "run", "--script", f"{SCRIPTS_REL}/{script}", *args],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
