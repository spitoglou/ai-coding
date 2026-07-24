"""Tests for adapt.py: toolchain detection + managed-block preservation."""

import shutil
import subprocess
import sys
from pathlib import Path

from conftest import CLAUDE_SRC

ADAPT_REL = ".claude/skills/agent-coordination/scripts/adapt.py"


def make_project(tmp_path: Path) -> Path:
    """A project copy with the core but no project.md yet."""
    shutil.copytree(CLAUDE_SRC, tmp_path / ".claude")
    (tmp_path / ".claude/project.md").unlink(missing_ok=True)
    return tmp_path


def run_adapt(project: Path):
    return subprocess.run(
        [sys.executable, ADAPT_REL], cwd=project, capture_output=True, text=True
    )


def profile(project: Path) -> str:
    return (project / ".claude/project.md").read_text()


def test_adapt_seeds_project_md_from_template(tmp_path: Path):
    project = make_project(tmp_path)
    (project / "pyproject.toml").write_text('[project]\nname = "demo-app"\n')
    r = run_adapt(project)
    assert r.returncode == 0, r.stderr
    text = profile(project)
    assert "**Type:** Python" in text
    assert "demo-app" in text
    assert "uv run pytest" in text


def test_adapt_detects_node(tmp_path: Path):
    project = make_project(tmp_path)
    (project / "package.json").write_text('{"name": "web-thing"}')
    run_adapt(project)
    text = profile(project)
    assert "**Type:** Node.js" in text
    assert "web-thing" in text
    assert "npm test" in text


def test_adapt_preserves_manual_notes_and_refreshes_block(tmp_path: Path):
    project = make_project(tmp_path)
    (project / "package.json").write_text('{"name": "web-thing"}')
    run_adapt(project)

    # Add a manual note below the managed block.
    md = project / ".claude/project.md"
    md.write_text(md.read_text().replace(
        "### Architecture\n", "### Architecture\n\nKEEP_ME: hexagonal, 3 adapters\n"
    ))

    # Switch toolchain and rerun.
    (project / "package.json").unlink()
    (project / "pyproject.toml").write_text('[project]\nname = "demo-app"\n')
    run_adapt(project)

    text = profile(project)
    assert "KEEP_ME: hexagonal, 3 adapters" in text          # note preserved
    assert "**Type:** Python" in text                        # block refreshed
    assert "Node.js" not in text                             # stale toolchain gone
    assert text.count("CORE:AUTODETECT:START") == 1          # no duplicate block


def test_adapt_unknown_toolchain_is_graceful(tmp_path: Path):
    project = make_project(tmp_path)
    r = run_adapt(project)
    assert r.returncode == 0, r.stderr
    assert "**Type:** Unknown" in profile(project)
