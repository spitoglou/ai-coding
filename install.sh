#!/usr/bin/env bash
# Install / update the AI Coding infrastructure into a target project.
#
# Copies the .claude/ toolkit into a target project, then bootstraps its
# runtime state. Runtime state (reports/_registry.md, _tech-debt.md) is never
# overwritten, so updating an existing install preserves local history.
#
# Usage:
#   ./install.sh <target-project-dir>
#   ./install.sh ../my-app
#
# Re-run any time to pull toolkit updates into a project.

set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-}"

if [ -z "$TARGET" ]; then
    echo "Usage: $0 <target-project-dir>" >&2
    exit 1
fi
if [ ! -d "$TARGET" ]; then
    echo "❌ Target is not a directory: $TARGET" >&2
    exit 1
fi

VERSION=$(cat "$SRC_DIR/.claude/VERSION" 2>/dev/null || echo "unknown")
echo "Installing AI Coding infrastructure v$VERSION → $TARGET"

# Copy the toolkit. Runtime report state is never copied, so existing
# registries and reports in the target are preserved; only templates ship.
# rsync runs without --delete, and the fallback copies source-side only, so
# neither path can remove the target's local report history.
mkdir -p "$TARGET/.claude/reports"
if command -v rsync >/dev/null 2>&1; then
    # Include rules must precede the catch-all exclude (first match wins).
    rsync -a \
        --include 'reports/' \
        --include 'reports/_registry-template.md' \
        --include 'reports/_tech-debt-template.md' \
        --exclude 'reports/*' \
        "$SRC_DIR/.claude/" "$TARGET/.claude/"
else
    # Fallback without rsync: copy every top-level item except reports/
    # wholesale, then copy only the report templates. The target's runtime
    # reports are never touched.
    for item in "$SRC_DIR/.claude/"*; do
        [ "$(basename "$item")" = "reports" ] && continue
        cp -R "$item" "$TARGET/.claude/"
    done
    for tmpl in _registry-template.md _tech-debt-template.md; do
        cp "$SRC_DIR/.claude/reports/$tmpl" "$TARGET/.claude/reports/" 2>/dev/null || true
    done
fi
echo "✅ Toolkit files copied"

# Bootstrap runtime state in the target (idempotent, non-destructive).
( cd "$TARGET" && bash .claude/skills/agent-coordination/scripts/bootstrap.sh )

echo "Done. Installed v$VERSION into $TARGET/.claude/"
