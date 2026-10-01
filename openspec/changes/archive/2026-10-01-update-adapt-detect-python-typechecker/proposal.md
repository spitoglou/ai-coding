# Change: Detect a Python project's type checker instead of assuming mypy

## Why
`adapt.py` set `uv run mypy .` as the type-check command for every project with a
`pyproject.toml`. Projects on basedpyright or pyright got a wrong AUTODETECT row plus a
hand-written override contradicting it, both loaded into every session (REQ-AIC-001,
from REQ-AUTH-011).

## What Changes
- Read `pyproject.toml` with `tomllib` and look for basedpyright, pyright or mypy in the
  dev dependencies (`[dependency-groups]`, `[tool.uv] dev-dependencies`,
  `[project.optional-dependencies]`, Poetry dev groups) and in `[tool.<checker>]` sections.
- A declared dependency outranks a bare `[tool.*]` section; among several, precedence is
  basedpyright, then pyright, then mypy.
- With none found, the row reads "(configure in Toolchain overrides)" instead of guessing.

## Impact
- Affected specs: `project-adaptation`
- Affected code: `.claude/skills/agent-coordination/scripts/adapt.py`, `tests/test_adapt.py`
- Python targets whose row changes get one AUTODETECT rewrite on their next session start.
