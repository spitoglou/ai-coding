"""Tests for validate_frontmatter.py.

Guards the failure mode behind the v0.2.1 bug report: a frontmatter block that
is not valid YAML is dropped silently, so the agent never registers ("Agent
type 'x' not found" mid-task) and a command falls back to its first body line
as its description.

The reported culprit was the `mode:` key, but `mode: scan | threat-model` is
perfectly valid YAML. The actual defect was the unquoted `: ` inside the
`description:` value — present in exactly the same 10 files, which is why the
correlation looked conclusive. These tests pin the real cause.
"""

from pathlib import Path

from conftest import run_script

AGENT = """---
name: {name}
description: {desc}
tools: Read
model: sonnet
{extra}---

Body.
"""


def write_agent(project: Path, name: str, desc: str = "Test agent.", extra: str = "") -> Path:
    path = project / ".claude/agents" / f"{name}.md"
    path.write_text(AGENT.format(name=name, desc=desc, extra=extra), encoding="utf-8")
    return path


def write_command(project: Path, name: str, frontmatter: str) -> Path:
    path = project / ".claude/commands" / f"{name}.md"
    path.write_text(f"---\n{frontmatter}---\n\n**Purpose**\n", encoding="utf-8")
    return path


def test_shipped_definitions_are_valid(project: Path):
    v = run_script(project, "validate_frontmatter.py")
    assert v.returncode == 0, v.stdout + v.stderr
    assert "✅" in v.stdout


def test_flags_unquoted_colon_in_description(project: Path):
    # The real root cause: YAML reads the second colon as another mapping key.
    write_agent(project, "sec", desc="Security review. Modes: scan (OWASP), compliance (SOC2).")
    v = run_script(project, "validate_frontmatter.py")
    assert v.returncode == 1
    assert "not valid YAML" in v.stdout
    assert "must be quoted" in v.stdout


def test_quoted_colon_in_description_is_accepted(project: Path):
    write_agent(project, "sec", desc='"Security review. Modes: scan (OWASP), compliance (SOC2)."')
    assert run_script(project, "validate_frontmatter.py").returncode == 0


def test_mode_key_is_reported_as_unsupported_not_as_a_yaml_error(project: Path):
    # `mode: scan | threat-model` parses fine — it is flagged on the key set,
    # which is a different (and much weaker) failure than a parse error.
    write_agent(project, "moded", extra="mode: scan | threat-model\n")
    v = run_script(project, "validate_frontmatter.py")
    assert v.returncode == 1
    assert "unsupported frontmatter key 'mode'" in v.stdout
    assert "not valid YAML" not in v.stdout


def test_flags_unquoted_colon_in_command_name(project: Path):
    # What actually broke /agents:review's description in the command list.
    write_command(project, "broken", "name: Agents: Review\ndescription: Review code.\n")
    v = run_script(project, "validate_frontmatter.py")
    assert v.returncode == 1
    assert "not valid YAML" in v.stdout


def test_flags_list_valued_argument_hint(project: Path):
    # `argument-hint: [days]` parses as a list, not the string the loader wants.
    write_command(project, "listy", "description: Archive things.\nargument-hint: [days]\n")
    v = run_script(project, "validate_frontmatter.py")
    assert v.returncode == 1
    assert "parsed as list" in v.stdout


def test_flags_unsupported_command_key(project: Path):
    write_command(project, "tagged", "description: Do a thing.\ntags: [a, b]\n")
    v = run_script(project, "validate_frontmatter.py")
    assert v.returncode == 1
    assert "unsupported frontmatter key 'tags'" in v.stdout


def test_flags_agent_name_filename_mismatch(project: Path):
    path = project / ".claude/agents/mismatch.md"
    path.write_text(AGENT.format(name="other", desc="x", extra=""), encoding="utf-8")
    v = run_script(project, "validate_frontmatter.py")
    assert v.returncode == 1
    assert "does not match filename stem" in v.stdout


def test_agent_without_frontmatter_is_an_error(project: Path):
    (project / ".claude/agents/bare.md").write_text("Just a body.\n", encoding="utf-8")
    v = run_script(project, "validate_frontmatter.py")
    assert v.returncode == 1
    assert "no frontmatter block" in v.stdout


def test_command_without_frontmatter_is_only_a_warning(project: Path):
    # A command still runs; it just loses its description in the command list.
    (project / ".claude/commands/bare.md").write_text("# Bare\n", encoding="utf-8")
    v = run_script(project, "validate_frontmatter.py")
    assert v.returncode == 0, v.stdout
    assert "no frontmatter block" in v.stdout
    assert run_script(project, "validate_frontmatter.py", "--strict").returncode == 1


def test_missing_model_is_a_warning_not_an_error(project: Path):
    (project / ".claude/agents/unpinned.md").write_text(
        "---\nname: unpinned\ndescription: x\ntools: Read\n---\n\nBody.\n", encoding="utf-8"
    )
    v = run_script(project, "validate_frontmatter.py")
    assert v.returncode == 0, v.stdout
    assert "no 'model' pin" in v.stdout
