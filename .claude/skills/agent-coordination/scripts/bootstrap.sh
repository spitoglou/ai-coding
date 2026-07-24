#!/usr/bin/env bash
# Bootstrap the agent-coordination runtime state in a project.
#
# Idempotent: safe to run repeatedly. Seeds the report registries from their
# templates (without overwriting existing ones) and creates the report
# category directories the commands expect.
#
# Usage: run from the project root (the directory that contains .claude/)
#   bash .claude/skills/agent-coordination/scripts/bootstrap.sh

set -euo pipefail

REPORTS_DIR=".claude/reports"

if [ ! -d ".claude" ]; then
    echo "❌ No .claude/ directory here. Run from the project root." >&2
    exit 1
fi

mkdir -p "$REPORTS_DIR"

TODAY=$(date +%Y-%m-%d)

seed_from_template() {
    local template="$1"
    local target="$2"
    if [ -f "$target" ]; then
        echo "• Exists, leaving as-is: $target"
    elif [ -f "$template" ]; then
        sed "s/YYYY-MM-DD/$TODAY/g" "$template" > "$target"
        echo "✅ Seeded: $target"
    else
        echo "⚠️  Template missing, skipped: $template" >&2
    fi
}

seed_from_template "$REPORTS_DIR/_registry-template.md" "$REPORTS_DIR/_registry.md"
seed_from_template "$REPORTS_DIR/_tech-debt-template.md" "$REPORTS_DIR/_tech-debt.md"

# Report category directories used across agents/commands.
CATEGORIES=(analysis architecture bugs commits design exec handoffs \
    implementation review tests security sre rfc ci archive)
for cat in "${CATEGORIES[@]}"; do
    mkdir -p "$REPORTS_DIR/$cat"
done
echo "✅ Ensured ${#CATEGORIES[@]} report category directories"

echo "Bootstrap complete."
