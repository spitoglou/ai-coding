#!/usr/bin/env bash
# Install / update the AI Coding infrastructure into a target project.
#
# Copies the generic .claude/ core into a target project, then bootstraps it.
# Project-owned files are NEVER overwritten, so updating an existing install
# preserves local history and adaptations:
#   - reports/*            runtime registries and reports (only templates ship)
#   - project.md           this project's specifics (adapt.sh generates it)
#   - settings.local.json  personal permissions (never copied out)
#
# Usage:
#   ./install.sh <target-project-dir>          install or update the core
#   ./install.sh --check <target-project-dir>  preview what an update would change
#
# Re-run any time to pull core updates; adaptations in project.md survive.

set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CHECK=0
if [ "${1:-}" = "--check" ]; then
    CHECK=1
    shift
fi
TARGET="${1:-}"

if [ -z "$TARGET" ]; then
    echo "Usage: $0 [--check] <target-project-dir>" >&2
    exit 1
fi
if [ ! -d "$TARGET" ]; then
    echo "❌ Target is not a directory: $TARGET" >&2
    exit 1
fi

VERSION=$(cat "$SRC_DIR/.claude/VERSION" 2>/dev/null || echo "unknown")

# Files that belong to the project, not the core: never copied/overwritten.
# (reports/ is handled separately so its templates can still ship.)
is_preserved() {  # is_preserved <basename>
    case "$1" in
        reports|project.md|settings.local.json) return 0 ;;
        *) return 1 ;;
    esac
}

# --- --check: read-only preview of an update --------------------------------
if [ "$CHECK" -eq 1 ]; then
    TARGET_VERSION=$(cat "$TARGET/.claude/VERSION" 2>/dev/null || echo "none")
    echo "Core version:   source v$VERSION  |  target v$TARGET_VERSION"
    echo "Changes an update would apply to the core (project.md/reports untouched):"
    # File-level diff, skipping project-owned paths. ~ changed, + new, - removed.
    diff_out=$(diff -rq \
        --exclude=reports \
        --exclude=project.md \
        --exclude=settings.local.json \
        "$SRC_DIR/.claude" "$TARGET/.claude" 2>/dev/null || true)
    if [ -z "$diff_out" ]; then
        echo "  (none — core is up to date)"
    else
        # ~ overwritten on update   + added on update   = your file, kept as-is
        echo "$diff_out" | sed \
            -e "s#^Files $SRC_DIR/.claude/\(.*\) and .* differ#  ~ \1 (overwritten)#" \
            -e "s#^Only in $SRC_DIR/.claude\(/*\)\(.*\): \(.*\)#  + \2\1\3 (added)#" \
            -e "s#^Only in $TARGET/.claude\(/*\)\(.*\): \(.*\)#  = \2\1\3 (yours, kept)#"
    fi
    echo "Legend: ~ overwritten by update   + added   = project file, left untouched"
    exit 0
fi

echo "Installing AI Coding infrastructure v$VERSION → $TARGET"

# Copy the core. rsync runs without --delete and the fallback copies
# source-side only, so neither path can remove project-owned files.
mkdir -p "$TARGET/.claude/reports"
if command -v rsync >/dev/null 2>&1; then
    # Include rules must precede the catch-all excludes (first match wins).
    rsync -a \
        --exclude 'settings.local.json' \
        --exclude 'project.md' \
        --include 'reports/' \
        --include 'reports/_registry-template.md' \
        --include 'reports/_tech-debt-template.md' \
        --exclude 'reports/*' \
        "$SRC_DIR/.claude/" "$TARGET/.claude/"
else
    # Fallback without rsync: copy every top-level core item, then only the
    # report templates. Project-owned files are never touched.
    for item in "$SRC_DIR/.claude/"*; do
        name="$(basename "$item")"
        is_preserved "$name" && continue
        cp -R "$item" "$TARGET/.claude/"
    done
    for tmpl in _registry-template.md _tech-debt-template.md; do
        cp "$SRC_DIR/.claude/reports/$tmpl" "$TARGET/.claude/reports/" 2>/dev/null || true
    done
fi
echo "✅ Core files copied"

# Bootstrap runtime state + adapt to the project (idempotent, non-destructive).
( cd "$TARGET" && bash .claude/skills/agent-coordination/scripts/bootstrap.sh )

echo "Done. Installed v$VERSION into $TARGET/.claude/"
