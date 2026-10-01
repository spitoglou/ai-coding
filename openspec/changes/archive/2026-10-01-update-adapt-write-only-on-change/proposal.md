# Change: adapt.py writes project.md only when a detected value changes

## Why
`adapt.py` runs at every session start in every target repository and rewrote the
`CORE:AUTODETECT` block unconditionally with today's date, so each new day left
`.claude/project.md` with a one-line diff that sessions had to revert before every
commit. On Windows it also wrote the whole file with CRLF line endings, raising a
line-ending warning on every run (REQ-AIC-002, from REQ-AUTH-008 and REQ-HWRT-008).

## What Changes
- Render the block with the date already recorded in the file and compare it with the
  block between the markers; write only when a detected value differs. The date moves
  together with the values, never on its own.
- A file whose markers hold no generated block yet (the seeded template) is still written.
- Writes keep the file's existing newline style instead of the platform default, and
  seeding `project.md` from the template copies its bytes unchanged.

## Impact
- Affected specs: `project-adaptation` (new capability)
- Affected code: `.claude/skills/agent-coordination/scripts/adapt.py`, `tests/test_adapt.py`
- Every target picks this up on its next `install.py` update; no migration needed.
