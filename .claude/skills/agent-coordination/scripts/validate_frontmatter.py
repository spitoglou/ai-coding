#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = ["pyyaml>=6"]
# ///
"""Validate the frontmatter of agent and command definitions.

Claude Code parses `.claude/agents/*.md` and `.claude/commands/**/*.md`
frontmatter as YAML. When a block fails to parse, the failure is silent: the
agent is simply absent from the registry (invoking it fails with "Agent type
'x' not found"), and the command falls back to using its first body line as
its description. Neither reports an error at startup, so the breakage is
usually discovered mid-task.

The most common cause is an unquoted value containing `: ` — YAML reads the
second colon as another mapping key and rejects the document:

    description: Security review. Modes: scan (OWASP)   # ScannerError
    description: "Security review. Modes: scan (OWASP)" # fine

This script parses each block with a real YAML parser (rather than guessing at
the syntax) and additionally checks the key sets, so this class of error fails
loudly at install time.

Usage:
    uv run --script validate_frontmatter.py [--claude-dir .claude] [--strict]

Exit code: 0 if no errors, 1 if any errors. With --strict, warnings also fail.
"""

import argparse
import sys
from pathlib import Path

import yaml

# Keys Claude Code accepts. Anything else is at best ignored and at worst
# grounds for rejecting the file — keep definitions to these. Extend when
# Claude Code adds a field; do not work around it by inventing keys.
AGENT_KEYS = {"name", "description", "tools", "model", "color"}
COMMAND_KEYS = {
    "description", "argument-hint", "allowed-tools", "model",
    "disable-model-invocation",
}

AGENT_REQUIRED = {"name", "description"}
COMMAND_REQUIRED = {"description"}

COLON_HINT = (
    "a value containing ': ' must be quoted — e.g. "
    'description: "Review. Modes: scan (OWASP)"'
)


def split_frontmatter(text: str) -> str | None:
    """Return the raw frontmatter block, or None if the file has none."""
    if not text.startswith("---"):
        return None
    parts = text.split("\n")
    try:
        end = next(i for i, line in enumerate(parts[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return ""  # opened but never closed; yaml will not see a valid block
    return "\n".join(parts[1:end])


def validate_file(path: Path, supported: set[str], required: set[str], is_agent: bool):
    """Return (errors, warnings) for one definition file."""
    errors: list[str] = []
    warnings: list[str] = []
    label = path.name if is_agent else path.as_posix()

    raw = split_frontmatter(path.read_text(encoding="utf-8"))
    if raw is None:
        msg = f"{label}: no frontmatter block (file must start with '---')"
        # An agent without frontmatter cannot register at all; a command still
        # works, it just loses its description in the command list.
        (errors if is_agent else warnings).append(msg)
        return errors, warnings
    if not raw.strip():
        errors.append(f"{label}: empty or unterminated frontmatter block")
        return errors, warnings

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        detail = str(exc).splitlines()[0]
        hint = f" — {COLON_HINT}" if ": " in raw else ""
        errors.append(f"{label}: frontmatter is not valid YAML ({detail}){hint}")
        return errors, warnings

    if not isinstance(data, dict):
        errors.append(f"{label}: frontmatter must be a mapping of keys to values")
        return errors, warnings

    for key in sorted(set(data) - supported):
        errors.append(
            f"{label}: unsupported frontmatter key '{key}' "
            f"(supported: {', '.join(sorted(supported))})"
        )
    for key in sorted(required - set(data)):
        errors.append(f"{label}: missing required frontmatter key '{key}'")

    for key in sorted(set(data) & supported):
        value = data[key]
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"{label}: frontmatter key '{key}' has an empty value")
        elif not isinstance(value, (str, bool)):
            # e.g. `argument-hint: [days]` parses as a list, not the string the
            # loader expects. Quote it.
            errors.append(
                f"{label}: frontmatter key '{key}' parsed as {type(value).__name__}, "
                f"not text — quote the value"
            )

    if is_agent:
        name = data.get("name")
        if isinstance(name, str) and name != path.stem:
            errors.append(
                f"{label}: name '{name}' does not match filename stem '{path.stem}' "
                f"— callers dispatch on the filename"
            )
        if "model" not in data:
            warnings.append(f"{label}: no 'model' pin; the agent inherits the session model")

    return errors, warnings


def validate(claude_dir: Path) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for every agent and command definition."""
    errors: list[str] = []
    warnings: list[str] = []

    agents_dir = claude_dir / "agents"
    commands_dir = claude_dir / "commands"
    if not agents_dir.is_dir() and not commands_dir.is_dir():
        return [f"Nothing to validate: no agents/ or commands/ under {claude_dir}"], []

    for path in sorted(agents_dir.glob("*.md")) if agents_dir.is_dir() else []:
        e, w = validate_file(path, AGENT_KEYS, AGENT_REQUIRED, is_agent=True)
        errors.extend(e)
        warnings.extend(w)

    for path in sorted(commands_dir.rglob("*.md")) if commands_dir.is_dir() else []:
        e, w = validate_file(path, COMMAND_KEYS, COMMAND_REQUIRED, is_agent=False)
        errors.extend(e)
        warnings.extend(w)

    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate agent/command frontmatter")
    parser.add_argument("--claude-dir", default=".claude")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args(argv)

    errors, warnings = validate(Path(args.claude_dir))

    for w in warnings:
        print(f"⚠️  {w}")
    for e in errors:
        print(f"❌ {e}")

    if not errors and not warnings:
        print("✅ Agent and command frontmatter is valid.")
    else:
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    # Windows defaults piped stdout/stderr to a legacy codepage (cp1252), which
    # makes the status glyphs above raise UnicodeEncodeError. Force UTF-8.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
