# Report Registry

**Last Updated:** YYYY-MM-DD

> **Purpose:** Central index. Check here first before new work.

---

## Entry Format

Every report is listed **exactly once**, as a table row under its category in
*All Reports by Category*. This is the one format `add_report.py`,
`validate_registry.py`, and `archive_reports.py` all parse:

```
| [name.md](category/name.md) | YYYY-MM-DD | Status | One-line summary |
```

Prefer the helper over hand-editing — it writes the row in the canonical shape:

```bash
uv run --script .claude/skills/agent-coordination/scripts/add_report.py \
    --category review --name review-quality-src --status Completed \
    --summary "Peer review of src/" --scaffold
```

Recency comes from the **Date** column, not from a separate section. Reports
older than the archive threshold are moved by `/archive` (see *Archive* below).

---

## Quick Links

- **Current Work:** [Active task or phase]
- **Latest Architecture:** [Most recent arch report]
- **Implementation Status:** [Current impl state]

---

## All Reports by Category

### Analysis
<!-- Research, EDA, data exploration -->

### Architecture
<!-- ADRs, system design -->

### Bugs
<!-- Bug reports, root cause analysis -->

### CI
<!-- CI pipeline results -->

### Commits
<!-- Commit summaries, changelogs -->

### Design
<!-- UI/UX reviews, design specs -->

### Docs
<!-- Documentation audits, coverage and accuracy reviews -->

### Exec
<!-- Execution logs, command outputs -->

### Handoffs
<!-- Agent coordination, context transfers -->

### Implementation
<!-- Code specs, impl plans -->

### Review
<!-- Code reviews, PR reviews -->

### RFC
<!-- Design proposals -->

### Security
<!-- Scans, threat models, compliance -->

### Sre
<!-- SLOs, postmortems, capacity -->

### Tests
<!-- Test plans, coverage reports -->

---

## Archive

Reports older than 7 days are moved by `/archive` to
`.claude/reports/archive/[category]/`, and their rows to a dated archive
registry: `.claude/reports/archive/_registry-archive-YYYY-MM-DD.md`.

Running `/archive` more than once on the same day **merges** into that day's
registry rather than replacing it.

---

## Legend

**Status Values** — the canonical set, defined in
`.claude/skills/agent-coordination/SKILL.md` and enforced by
`validate_registry.py`:

- **Active** — Current, in use
- **Completed** — Done, no changes expected
- **Superseded** — Replaced by newer report
- **Archived** — Historical reference only (set by `/archive`)
