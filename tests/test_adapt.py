"""Tests for adapt.py: toolchain detection + managed-block preservation."""

import os
import re
import shutil
import subprocess
from datetime import date
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
        ["uv", "run", "--script", ADAPT_REL], cwd=project, capture_output=True,
        text=True, encoding="utf-8",
    )


def profile(project: Path) -> str:
    return (project / ".claude/project.md").read_text(encoding="utf-8")


def test_adapt_seeds_project_md_from_template(tmp_path: Path):
    project = make_project(tmp_path)
    (project / "pyproject.toml").write_text('[project]\nname = "demo-app"\n', encoding="utf-8")
    r = run_adapt(project)
    assert r.returncode == 0, r.stderr
    text = profile(project)
    assert "**Type:** Python" in text
    assert "demo-app" in text
    assert "uv run pytest" in text


def test_adapt_detects_node(tmp_path: Path):
    project = make_project(tmp_path)
    (project / "package.json").write_text('{"name": "web-thing"}', encoding="utf-8")
    run_adapt(project)
    text = profile(project)
    assert "**Type:** Node.js" in text
    assert "web-thing" in text
    assert "npm test" in text


def test_adapt_preserves_manual_notes_and_refreshes_block(tmp_path: Path):
    project = make_project(tmp_path)
    (project / "package.json").write_text('{"name": "web-thing"}', encoding="utf-8")
    run_adapt(project)

    # Add a manual note below the managed block.
    md = project / ".claude/project.md"
    md.write_text(md.read_text(encoding="utf-8").replace(
        "### Architecture\n", "### Architecture\n\nKEEP_ME: hexagonal, 3 adapters\n"
    ), encoding="utf-8")

    # Switch toolchain and rerun.
    (project / "package.json").unlink()
    (project / "pyproject.toml").write_text('[project]\nname = "demo-app"\n', encoding="utf-8")
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


# --- Write only on a real change (REQ-AIC-002) --------------------------------

OLD_DATE = "2020-01-02"


def backdate(project: Path) -> Path:
    """Move the recorded date into the past and the file's mtime with it."""
    md = project / ".claude/project.md"
    text = md.read_bytes().decode("utf-8")
    text = re.sub(r"_Auto-detected \d{4}-\d{2}-\d{2}\.", f"_Auto-detected {OLD_DATE}.", text)
    md.write_bytes(text.encode("utf-8"))
    os.utime(md, ns=(1_000_000_000, 1_000_000_000))
    return md


def test_adapt_unchanged_toolchain_does_not_write(tmp_path: Path):
    project = make_project(tmp_path)
    (project / "pyproject.toml").write_text('[project]\nname = "demo-app"\n', encoding="utf-8")
    run_adapt(project)
    md = backdate(project)
    before = md.read_bytes()

    r = run_adapt(project)
    assert r.returncode == 0, r.stderr
    assert md.read_bytes() == before                   # date did not move on its own
    assert md.stat().st_mtime_ns == 1_000_000_000      # file not even rewritten
    assert "already current" in r.stdout


def test_adapt_changed_toolchain_writes_new_date(tmp_path: Path):
    project = make_project(tmp_path)
    (project / "package.json").write_text('{"name": "web-thing"}', encoding="utf-8")
    run_adapt(project)
    backdate(project)

    (project / "package.json").write_text('{"name": "renamed-thing"}', encoding="utf-8")
    run_adapt(project)
    text = profile(project)
    assert "renamed-thing" in text
    assert f"_Auto-detected {date.today().isoformat()}." in text
    assert OLD_DATE not in text


def test_adapt_writes_block_when_absent(tmp_path: Path):
    project = make_project(tmp_path)
    (project / "pyproject.toml").write_text('[project]\nname = "demo-app"\n', encoding="utf-8")
    shutil.copy(project / ".claude/project-template.md", project / ".claude/project.md")
    run_adapt(project)
    text = profile(project)
    assert "**Type:** Python" in text
    assert f"_Auto-detected {date.today().isoformat()}." in text


def test_adapt_consecutive_runs_are_byte_identical(tmp_path: Path):
    project = make_project(tmp_path)
    (project / "pyproject.toml").write_text('[project]\nname = "demo-app"\n', encoding="utf-8")
    run_adapt(project)
    first = (project / ".claude/project.md").read_bytes()
    run_adapt(project)
    assert (project / ".claude/project.md").read_bytes() == first


def test_adapt_keeps_lf_newlines(tmp_path: Path):
    project = make_project(tmp_path)
    (project / ".claude/project.md").write_bytes(
        (project / ".claude/project-template.md").read_bytes().replace(b"\r\n", b"\n"))
    (project / "pyproject.toml").write_text('[project]\nname = "demo-app"\n', encoding="utf-8")
    run_adapt(project)
    data = (project / ".claude/project.md").read_bytes()
    assert b"**Type:** Python" in data
    assert b"\r\n" not in data


def test_adapt_keeps_crlf_newlines(tmp_path: Path):
    project = make_project(tmp_path)
    lf = (project / ".claude/project-template.md").read_bytes().replace(b"\r\n", b"\n")
    (project / ".claude/project.md").write_bytes(lf.replace(b"\n", b"\r\n"))
    (project / "pyproject.toml").write_text('[project]\nname = "demo-app"\n', encoding="utf-8")
    run_adapt(project)
    data = (project / ".claude/project.md").read_bytes()
    assert b"**Type:** Python" in data
    assert data.count(b"\n") == data.count(b"\r\n")      # no bare LF introduced


# --- Python type checker detection (REQ-AIC-001) -------------------------------

def typecheck_row(project: Path) -> str:
    return next(line for line in profile(project).splitlines() if line.startswith("| Type check |"))


def adapt_pyproject(tmp_path: Path, body: str) -> str:
    project = make_project(tmp_path)
    (project / "pyproject.toml").write_text('[project]\nname = "demo-app"\n' + body, encoding="utf-8")
    r = run_adapt(project)
    assert r.returncode == 0, r.stderr
    return typecheck_row(project)


def test_typecheck_basedpyright_in_dependency_groups(tmp_path: Path):
    row = adapt_pyproject(tmp_path, '[dependency-groups]\ndev = ["basedpyright>=1.22.0", "pytest"]\n')
    assert "`uv run basedpyright`" in row


def test_typecheck_pyright_in_optional_dependencies(tmp_path: Path):
    row = adapt_pyproject(tmp_path, '[project.optional-dependencies]\ndev = ["Pyright[nodejs]==1.1"]\n')
    assert "`uv run pyright`" in row


def test_typecheck_mypy_in_uv_dev_dependencies(tmp_path: Path):
    row = adapt_pyproject(tmp_path, '[tool.uv]\ndev-dependencies = ["mypy>=1.0", "types-requests"]\n')
    assert "`uv run mypy .`" in row


def test_typecheck_mypy_in_poetry_group(tmp_path: Path):
    row = adapt_pyproject(tmp_path, '[tool.poetry.group.dev.dependencies]\nmypy = "^1.0"\n')
    assert "`uv run mypy .`" in row


def test_typecheck_from_tool_section_only(tmp_path: Path):
    row = adapt_pyproject(tmp_path, '[tool.mypy]\nstrict = true\n')
    assert "`uv run mypy .`" in row


def test_typecheck_none_is_neutral(tmp_path: Path):
    row = adapt_pyproject(tmp_path, '[dependency-groups]\ndev = ["pytest", "types-requests"]\n')
    assert "configure in Toolchain overrides" in row
    assert "mypy" not in row


def test_typecheck_more_than_one_uses_precedence(tmp_path: Path):
    row = adapt_pyproject(tmp_path, '[dependency-groups]\ndev = ["mypy", "basedpyright"]\n')
    assert "`uv run basedpyright`" in row


def test_typecheck_dependency_outranks_tool_section(tmp_path: Path):
    # basedpyright reads [tool.pyright] too, so that section must not win.
    row = adapt_pyproject(tmp_path, '[dependency-groups]\ndev = ["basedpyright"]\n\n[tool.pyright]\nstrict = ["src"]\n')
    assert "`uv run basedpyright`" in row
