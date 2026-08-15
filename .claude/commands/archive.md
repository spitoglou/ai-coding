---
description: Archive old registry entries and reports (run weekly or when registry > 50 entries)
allowed-tools: Bash, Read, Write, Edit
argument-hint: "[days]"
---

# Archive Registry

Move registry entries and reports older than N days to archive.

REPORTS_DIR=".claude/reports"
ARCHIVE_DIR="$REPORTS_DIR/archive"
REGISTRY="$REPORTS_DIR/_registry.md"

## Process

1. **Parse active registry** for entries older than threshold (default: 7 days).
   Rows must be in the canonical format (see `SKILL.md` § *Registry Entry
   Format*); the script refuses to run if it can parse none of them.
2. **Move report files** to `.claude/reports/archive/[category]/`
3. **Write the dated archive registry** `.claude/reports/archive/_registry-archive-YYYY-MM-DD.md`,
   merging with that day's registry if one already exists
4. **Update active registry** (remove archived entries)
5. **Set status** of archived entries to "Archived" in dated registry
6. **Report summary** with archive date, entry-line counts, and file count

## Arguments

- `$ARGUMENTS`: Days threshold (default: 7)
  - `/archive` - Archive entries older than 7 days
  - `/archive 14` - Archive entries older than 14 days
  - `/archive 3` - Archive entries older than 3 days

## Archive Structure

```
.claude/reports/archive/
├── _registry-archive-YYYY-MM-DD.md  # Dated archive registry (one per archive day)
├── analysis/                        # Old analysis reports
├── architecture/                    # Old architecture reports
├── bugs/                            # Old bug reports
├── ci/                              # Old CI reports
├── commits/                         # Old commit reports
├── design/                          # Old design reports
├── docs/                            # Old documentation reports
├── exec/                            # Old execution reports
├── handoffs/                        # Old handoff reports
├── implementation/                  # Old implementation reports
├── review/                          # Old review reports
├── rfc/                             # Old RFCs
├── security/                        # Old security reports
├── sre/                             # Old SRE reports
└── tests/                           # Old test reports
```

Category subdirectories are created on demand — only categories that actually
have archived reports appear.

## Execution

Uses the archive script bundled with the agent-coordination skill:

```bash
# Run with UV (Python projects)
uv run --script .claude/skills/agent-coordination/scripts/archive_reports.py [days]

# Examples
uv run --script .claude/skills/agent-coordination/scripts/archive_reports.py     # Default: 7 days
uv run --script .claude/skills/agent-coordination/scripts/archive_reports.py 14  # 14 days
uv run --script .claude/skills/agent-coordination/scripts/archive_reports.py 7 --dry-run  # Preview only
```

## When to Run

- **Weekly:** As part of end-of-week cleanup
- **On demand:** When registry exceeds ~50 active entries
- **Before major work:** To ensure clean context

## Notes

- **Dated registries:** Each archive *day* has one `_registry-archive-YYYY-MM-DD.md`
- **Same-day runs merge:** A second run on the same day merges into that day's
  registry rather than replacing it, so an earlier batch is never orphaned
  (its files would otherwise sit in `archive/` with no row in any registry)
- **Full automation:** Updates both active and archive registries automatically
- **Archived reports** remain accessible in archive folder by category
- **Reversible:** Can be reversed by moving entries back
- **No deletion:** Does NOT delete anything - only moves
- **Archive history:** Track all past archives via dated registry files
