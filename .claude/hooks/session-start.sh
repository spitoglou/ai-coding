#!/usr/bin/env bash
# SessionStart hook: keep the agent-coordination runtime state self-healing.
#
# Runs the idempotent bootstrap so a freshly-ported project (or one whose
# reports/ was cleaned) always has its registries and report directories before
# any command needs them. Never blocks the session: any failure is swallowed.
#
# Registered in .claude/settings.json. Remove that entry to disable.

set -u

BOOTSTRAP=".claude/skills/agent-coordination/scripts/bootstrap.sh"

if [ -f "$BOOTSTRAP" ]; then
    if bash "$BOOTSTRAP" >/dev/null 2>&1; then
        echo "agent-coordination: runtime state ready (.claude/reports)"
    fi
fi

exit 0
