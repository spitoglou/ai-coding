#!/usr/bin/env bash
# Adapt the toolkit's generic core to this project (deterministic pass).
#
# Seeds .claude/project.md from the template if missing, then regenerates ONLY
# the <!-- CORE:AUTODETECT --> block with the project's detected toolchain.
# Everything outside that block (your "Project-specific notes") is preserved.
#
# Idempotent and rerunnable. The richer, judgement-based adaptation (filling in
# architecture/conventions/domain) is done by the `/adapt` command.
#
# Usage: run from the project root
#   bash .claude/skills/agent-coordination/scripts/adapt.sh

set -euo pipefail

CLAUDE_DIR=".claude"
PROJECT_MD="$CLAUDE_DIR/project.md"
TEMPLATE="$CLAUDE_DIR/project-template.md"
START="<!-- CORE:AUTODETECT:START -->"
END="<!-- CORE:AUTODETECT:END -->"

if [ ! -d "$CLAUDE_DIR" ]; then
    echo "❌ No .claude/ directory here. Run from the project root." >&2
    exit 1
fi

# --- Seed project.md from template on first run ------------------------------
if [ ! -f "$PROJECT_MD" ]; then
    if [ -f "$TEMPLATE" ]; then
        cp "$TEMPLATE" "$PROJECT_MD"
        echo "✅ Created $PROJECT_MD from template"
    else
        echo "❌ Template missing: $TEMPLATE" >&2
        exit 1
    fi
fi

# --- Detect toolchain --------------------------------------------------------
TYPE="Unknown"; PM="n/a"
TEST="(configure in Toolchain overrides)"; LINT="$TEST"; TYPECHECK="$TEST"; BUILD="$TEST"
NAME="$(basename "$(pwd)")"

read_field() {  # read_field <file> <regex-capturing-value>
    sed -n "s/$2/\1/p" "$1" 2>/dev/null | head -1
}

if [ -f pyproject.toml ]; then
    TYPE="Python"; PM="uv"
    TEST="uv run pytest"; LINT="uv run ruff check ."
    TYPECHECK="uv run mypy ."; BUILD="uv build"
    n="$(read_field pyproject.toml '^name = "\(.*\)"')"; [ -n "$n" ] && NAME="$n"
elif [ -f package.json ]; then
    TYPE="Node.js"; PM="npm"
    TEST="npm test"; LINT="npm run lint"
    TYPECHECK="npm run typecheck"; BUILD="npm run build"
    n="$(read_field package.json '.*"name": *"\([^"]*\)".*')"; [ -n "$n" ] && NAME="$n"
elif [ -f Cargo.toml ]; then
    TYPE="Rust"; PM="cargo"
    TEST="cargo test"; LINT="cargo clippy"
    TYPECHECK="cargo check"; BUILD="cargo build --release"
    n="$(read_field Cargo.toml '^name = "\(.*\)"')"; [ -n "$n" ] && NAME="$n"
elif [ -f go.mod ]; then
    TYPE="Go"; PM="go"
    TEST="go test ./..."; LINT="golangci-lint run"
    TYPECHECK="go vet ./..."; BUILD="go build ./..."
    n="$(read_field go.mod '^module \(.*\)')"; [ -n "$n" ] && NAME="$(basename "$n")"
fi

TODAY="$(date +%Y-%m-%d)"

# --- Build the managed block -------------------------------------------------
BLOCK_FILE="$(mktemp)"
trap 'rm -f "$BLOCK_FILE"' EXIT
cat > "$BLOCK_FILE" <<EOF
**Project:** $NAME
**Type:** $TYPE
**Package manager:** $PM

| Task | Command |
|------|---------|
| Test | \`$TEST\` |
| Lint | \`$LINT\` |
| Type check | \`$TYPECHECK\` |
| Build | \`$BUILD\` |

_Auto-detected $TODAY. Override any wrong value under "Toolchain overrides" below._
EOF

# --- Splice the block between the markers, preserving everything else --------
if ! grep -qF "$START" "$PROJECT_MD" || ! grep -qF "$END" "$PROJECT_MD"; then
    echo "❌ $PROJECT_MD is missing the CORE:AUTODETECT markers." >&2
    echo "   Restore them from $TEMPLATE (or delete project.md to reseed)." >&2
    exit 1
fi

awk -v start="$START" -v end="$END" -v blockfile="$BLOCK_FILE" '
    index($0, start) { print; while ((getline l < blockfile) > 0) print l; close(blockfile); skip=1; next }
    index($0, end)   { skip=0; print; next }
    skip != 1        { print }
' "$PROJECT_MD" > "$PROJECT_MD.tmp"
mv "$PROJECT_MD.tmp" "$PROJECT_MD"

echo "✅ Adapted core to: $NAME ($TYPE) — refreshed AUTODETECT block in $PROJECT_MD"
