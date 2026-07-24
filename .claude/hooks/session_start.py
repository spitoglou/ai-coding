#!/usr/bin/env python3
"""SessionStart hook: keep the agent-coordination runtime state self-healing.

Cross-platform replacement for session-start.sh. Runs the idempotent bootstrap
so a freshly-ported project (or one whose reports/ was cleaned) always has its
registries and report directories before any command needs them. Never blocks
the session: any failure is swallowed.

Registered in .claude/settings.json. Remove that entry to disable.
"""

import subprocess
import sys
from pathlib import Path

BOOTSTRAP = Path(".claude/skills/agent-coordination/scripts/bootstrap.py")


def main() -> int:
    if BOOTSTRAP.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(BOOTSTRAP)],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                print("agent-coordination: runtime state ready (.claude/reports)")
        except Exception:
            pass  # never block the session
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
