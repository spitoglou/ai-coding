#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
"""Install / update the AI Coding infrastructure into a target project.

Cross-platform replacement for install.sh. Copies the generic .claude/ core
into a target project, then bootstraps it. Project-owned files are NEVER
overwritten, so updating an existing install preserves local history and
adaptations:
    - reports/*            runtime registries and reports (only templates ship)
    - project.md           this project's specifics (adapt.py generates it)
    - settings.local.json  personal permissions (never copied out)

Usage:
    uv run --script install.py <target-project-dir>           install or update the core
    uv run --script install.py --check <target-project-dir>   preview what would change

Re-run any time to pull core updates; adaptations in project.md survive.
"""

import argparse
import filecmp
import shutil
import subprocess
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
SRC_CLAUDE = SRC_DIR / ".claude"

# Files/dirs that belong to the project, not the core: never copied/overwritten.
PRESERVED = {"reports", "project.md", "settings.local.json"}
REPORT_TEMPLATES = ("_registry-template.md", "_tech-debt-template.md")


def read_version() -> str:
    try:
        return (SRC_CLAUDE / "VERSION").read_text().strip()
    except OSError:
        return "unknown"


def diff_tree(left: Path, right: Path, rel: Path = Path(".")):
    """Yield (status, relpath) for core differences, skipping preserved names.

    status: 'changed' (differs), 'added' (in source only), 'kept' (target only).
    """
    ignore = list(PRESERVED) if rel == Path(".") else []
    cmp = filecmp.dircmp(left, right, ignore=ignore)
    for name in cmp.diff_files:
        yield "changed", rel / name
    for name in cmp.left_only:
        yield "added", rel / name
    for name in cmp.right_only:
        yield "kept", rel / name
    for name in cmp.common_dirs:
        yield from diff_tree(left / name, right / name, rel / name)


def do_check(target_claude: Path) -> int:
    target_version = "none"
    vfile = target_claude / "VERSION"
    if vfile.exists():
        target_version = vfile.read_text().strip()

    print(f"Core version:   source v{read_version()}  |  target v{target_version}")
    print("Changes an update would apply to the core (project.md/reports untouched):")

    label = {
        "changed": "~ {} (overwritten)",
        "added": "+ {} (added)",
        "kept": "= {} (yours, kept)",
    }
    rows = sorted(diff_tree(SRC_CLAUDE, target_claude), key=lambda x: str(x[1]))
    if not rows:
        print("  (none — core is up to date)")
    else:
        for status, path in rows:
            print("  " + label[status].format(path.as_posix()))
    print("Legend: ~ overwritten by update   + added   = project file, left untouched")
    return 0


def do_install(target_claude: Path) -> int:
    version = read_version()
    print(f"Installing AI Coding infrastructure v{version} → {target_claude.parent}")

    (target_claude / "reports").mkdir(parents=True, exist_ok=True)

    # Copy every top-level core item; skip project-owned files. copytree with
    # dirs_exist_ok merges (overwriting core files) without deleting extras.
    for item in sorted(SRC_CLAUDE.iterdir()):
        if item.name in PRESERVED:
            continue
        dest = target_claude / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)

    # Ship only the report templates from reports/.
    for tmpl in REPORT_TEMPLATES:
        src = SRC_CLAUDE / "reports" / tmpl
        if src.exists():
            shutil.copy2(src, target_claude / "reports" / tmpl)
    print("✅ Core files copied")

    # Bootstrap runtime state + adapt (idempotent, non-destructive).
    subprocess.run(
        ["uv", "run", "--script", ".claude/skills/agent-coordination/scripts/bootstrap.py"],
        cwd=target_claude.parent, check=True,
    )
    print(f"Done. Installed v{version} into {target_claude}/")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install/update the toolkit core")
    parser.add_argument("--check", action="store_true", help="Preview changes; write nothing")
    parser.add_argument("target", help="Target project directory")
    args = parser.parse_args(argv)

    target = Path(args.target)
    if not target.is_dir():
        print(f"❌ Target is not a directory: {target}", file=sys.stderr)
        return 1

    target_claude = target / ".claude"
    if args.check:
        return do_check(target_claude)
    return do_install(target_claude)


if __name__ == "__main__":
    raise SystemExit(main())
