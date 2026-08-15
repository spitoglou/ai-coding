# Agent Coordination Templates

Load this file when creating reports or handoffs.

---

## Category Quick Reference

Filenames follow `[category]-[topic]-[scope]-YYYY-MM-DD.md` — see *Report
Naming* in `SKILL.md` for the scope slug rules.

| Category | Use For | Example Filename |
|----------|---------|------------------|
| `analysis/` | Research, EDA, data exploration | `analysis-user-behavior-all-2025-12-16.md` |
| `architecture/` | Architecture decisions, ADRs, system design | `architecture-api-redesign-src-api-2025-12-16.md` |
| `bugs/` | Bug reports, root cause analysis | `bugs-login-failure-src-auth-2025-12-16.md` |
| `ci/` | CI pipeline results | `ci-pipeline-main-all-2025-12-16.md` |
| `commits/` | Commit summaries, changelog entries | `commits-release-v2-all-2025-12-16.md` |
| `design/` | UI/UX reviews, design specs | `design-dashboard-review-src-ui-2025-12-16.md` |
| `docs/` | Documentation audits, coverage and accuracy reviews | `docs-readme-accuracy-all-2025-12-16.md` |
| `exec/` | Execution logs, command outputs | `exec-migration-all-2025-12-16.md` |
| `handoffs/` | Agent coordination, context transfers | `handoffs-architecture-to-backend-src-2025-12-16.md` |
| `implementation/` | Implementation plans, code specs | `implementation-auth-module-src-auth-2025-12-16.md` |
| `review/` | Code reviews, PR reviews | `review-pr-123-src-2025-12-16.md` |
| `rfc/` | Design proposals, RFCs | `rfc-0001-auth-system-all-2025-12-16.md` |
| `security/` | Security scans, threat models, compliance | `security-scan-src-api-2025-12-16.md` |
| `sre/` | SLOs, postmortems, capacity plans | `sre-postmortem-outage-all-2025-12-16.md` |
| `tests/` | Test plans, test results, coverage | `tests-auth-coverage-src-auth-2025-12-16.md` |

---

## Report Template

The header block is what `add_report.py --scaffold` writes, so a scaffolded
report starts compliant. Commands that produce reports by hand should reproduce
it. Status values are the canonical set defined in `SKILL.md` — `Draft` is not
one of them; an in-progress report is `Active`.

```markdown
# [Category]: [Topic]

**Agent:** [Agent Name]
**Date:** YYYY-MM-DD
**Status:** Active | Completed | Superseded | Archived

---

## Summary
[2-4 sentences: what was done, key findings, outcome]

---

## Key Decisions
- **[Decision 1]:** [What + Why]
- **[Decision 2]:** [What + Why]

---

## Details
[Main content - organized with headers]

---

## Action Items

### For [Agent/Role]:
- [ ] [Task] (Priority: High/Med/Low)

---

## Dependencies
**Depends on:** [report.md] - [Why]
**Blocks:** [What needs this first]

---

## References
- [report.md] - [How it relates]
```

---

## Handoff Template

Use for agent-to-agent coordination:

```markdown
# Handoff: [From Agent] → [To Agent]

**Topic:** [What's being handed off]
**Date:** YYYY-MM-DD

---

## Context
[Background the receiving agent needs]

## Completed Work
- [What was done]
- [Decisions made]

## Action Items for [To Agent]
- [ ] [Specific task with acceptance criteria]
- [ ] [Another task]

## Must Read
- This report: [Specific sections]
- Related: [other-report.md]

## Success Criteria
- [How to verify completion]
```

---

## Registry Entry Format

Defined in `SKILL.md` § *Registry Entry Format* — that section governs; this is
a pointer, not a second definition. One table row per report, under its category
heading in `## All Reports by Category`:

```markdown
| [name.md](category/name.md) | YYYY-MM-DD | Status | Summary in one line |
```

Write it with the helper rather than by hand:

```bash
uv run --script .claude/skills/agent-coordination/scripts/add_report.py \
    --category review --name review-quality-src \
    --status Completed --summary "Peer review of src/" --scaffold
```

---

## Task Prompt Template

For invoking agents with full context:

```
Task(agent-name, "
**Objective:** [Clear goal]

**Context from registry:**
- [Report 1]: [Key decision/finding]
- [Report 2]: [Relevant constraint]
- Current state: [What exists now]

**Requirements:**
1. [Specific deliverable]
2. [Another deliverable]

**Files to work with:**
- path/to/file1
- path/to/file2

**Expected output:**
- Report: .claude/reports/[category]/[category]-[topic]-[scope]-YYYY-MM-DD.md
- Code: [path if applicable]
- Success: [How to verify]

**Mode:** [If agent has modes: specify which]
")
```

---

## OpenSpec Integration

### When Reports Relate to OpenSpec

Add OpenSpec reference to report header when applicable:

```markdown
# [Category]: [Topic]

**Agent:** [Agent Name]
**Date:** YYYY-MM-DD
**Status:** Completed
**OpenSpec Change:** [change-id](../../openspec/changes/[change-id]/)

---
```

### Report Category → OpenSpec Mapping

| Report Category | OpenSpec Relationship |
|-----------------|----------------------|
| `rfc/` | May become OpenSpec proposal if proposing changes |
| `architecture/` | Can feed into OpenSpec `design.md` files |
| `review/` | Evidence for OpenSpec pre-archive quality checks |
| `security/` | May trigger OpenSpec security-related proposals |
| `tests/` | Verification for OpenSpec implementation |

### OpenSpec Verification Report Template

For pre-archive verification (link in OpenSpec `tasks.md`):

```markdown
# Verification: [OpenSpec Change ID]

**Agent:** [Agent Name]
**Date:** YYYY-MM-DD
**OpenSpec Change:** [change-id](../../openspec/changes/[change-id]/)
**Status:** Completed

---

## Scope
Files/areas reviewed for this OpenSpec change:
- [file1.py]
- [file2.py]

## Findings

### Critical (Must Fix Before Archive)
- None | [List issues]

### High (Should Fix)
- None | [List issues]

### Medium/Low (Track as Tech Debt)
- None | [List issues with TD-NNN references]

## Verdict
- [ ] **APPROVED** - Safe to archive
- [ ] **BLOCKED** - Issues must be resolved first

## Notes
[Any additional context for the OpenSpec change owner]
```

### Tech Debt Entry with OpenSpec Link

When creating tech debt from agent findings related to an OpenSpec change:

```markdown
- [ ] **TD-NNN**: [Description]
  - **Impact:** [Critical|High|Medium|Low]
  - **Source:** [report-name.md](category/report-name.md)
  - **OpenSpec:** [change-id](../../openspec/changes/[change-id]/)
  - **Created:** YYYY-MM-DD
```
