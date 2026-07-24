#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
"""Adapt the toolkit's generic core to this project (deterministic pass).

Cross-platform replacement for adapt.sh. Seeds .claude/project.md from the
template if missing, then regenerates ONLY the <!-- CORE:AUTODETECT --> block
with the project's detected toolchain. Everything outside that block (your
"Project-specific notes") is preserved.

Idempotent and rerunnable. The richer, judgement-based adaptation is done by the
`/adapt` command.

Usage: run from the project root
    uv run --script adapt.py
"""

import re
import sys
from datetime import date as date_cls
from pathlib import Path

START = "<!-- CORE:AUTODETECT:START -->"
END = "<!-- CORE:AUTODETECT:END -->"

UNKNOWN_CMD = "(configure in Toolchain overrides)"


def detect_toolchain(root: Path) -> dict:
    """Return toolchain facts detected from config files in root."""
    name = root.resolve().name

    def field(path: Path, pattern: str) -> str | None:
        try:
            m = re.search(pattern, path.read_text(), re.MULTILINE)
            return m.group(1) if m else None
        except OSError:
            return None

    if (root / "pyproject.toml").exists():
        info = dict(type="Python", pm="uv", test="uv run pytest",
                    lint="uv run ruff check .", typecheck="uv run mypy .", build="uv build")
        info["name"] = field(root / "pyproject.toml", r'^name = "(.*)"') or name
    elif (root / "package.json").exists():
        info = dict(type="Node.js", pm="npm", test="npm test",
                    lint="npm run lint", typecheck="npm run typecheck", build="npm run build")
        info["name"] = field(root / "package.json", r'"name"\s*:\s*"([^"]*)"') or name
    elif (root / "Cargo.toml").exists():
        info = dict(type="Rust", pm="cargo", test="cargo test",
                    lint="cargo clippy", typecheck="cargo check", build="cargo build --release")
        info["name"] = field(root / "Cargo.toml", r'^name = "(.*)"') or name
    elif (root / "go.mod").exists():
        module = field(root / "go.mod", r"^module (.*)")
        info = dict(type="Go", pm="go", test="go test ./...",
                    lint="golangci-lint run", typecheck="go vet ./...", build="go build ./...")
        info["name"] = module.split("/")[-1] if module else name
    else:
        info = dict(type="Unknown", pm="n/a", test=UNKNOWN_CMD,
                    lint=UNKNOWN_CMD, typecheck=UNKNOWN_CMD, build=UNKNOWN_CMD, name=name)
    return info


def build_block(info: dict, today: str) -> str:
    """Render the managed AUTODETECT block body (between the markers)."""
    return (
        f"**Project:** {info['name']}\n"
        f"**Type:** {info['type']}\n"
        f"**Package manager:** {info['pm']}\n\n"
        "| Task | Command |\n"
        "|------|---------|\n"
        f"| Test | `{info['test']}` |\n"
        f"| Lint | `{info['lint']}` |\n"
        f"| Type check | `{info['typecheck']}` |\n"
        f"| Build | `{info['build']}` |\n\n"
        f'_Auto-detected {today}. Override any wrong value under "Toolchain overrides" below._\n'
    )


def splice_block(text: str, block: str) -> str:
    """Replace the content between START/END markers with `block`."""
    start_i = text.index(START) + len(START)
    end_i = text.index(END)
    return text[:start_i] + "\n" + block + text[end_i:]


def main() -> int:
    claude_dir = Path(".claude")
    project_md = claude_dir / "project.md"
    template = claude_dir / "project-template.md"

    if not claude_dir.is_dir():
        print("❌ No .claude/ directory here. Run from the project root.", file=sys.stderr)
        return 1

    if not project_md.exists():
        if not template.exists():
            print(f"❌ Template missing: {template}", file=sys.stderr)
            return 1
        project_md.write_text(template.read_text())
        print(f"✅ Created {project_md} from template")

    text = project_md.read_text()
    if START not in text or END not in text:
        print(f"❌ {project_md} is missing the CORE:AUTODETECT markers.", file=sys.stderr)
        print(f"   Restore them from {template} (or delete project.md to reseed).", file=sys.stderr)
        return 1

    info = detect_toolchain(Path("."))
    block = build_block(info, date_cls.today().isoformat())
    project_md.write_text(splice_block(text, block))

    print(f"✅ Adapted core to: {info['name']} ({info['type']}) — refreshed AUTODETECT block in {project_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
