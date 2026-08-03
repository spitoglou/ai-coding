---
description: Multi-level code review with peer, architecture, security, and reliability checks.
argument-hint: <path> [--quick|--security|--all]
allowed-tools: Read, Write, Glob, Grep, Bash, Task
---

# Full Review Protocol

Multi-level code review following enterprise engineering standards.

**Before proceeding:** Read the `agent-coordination` skill at `.claude/skills/agent-coordination/SKILL.md` for registry management, verification scripts, and coordination protocols. This command follows its **Report Naming** and **Finding Severity** rules exactly — that is what makes each level's output interchangeable with the single-purpose command that produces the same report.

**Level ≡ command equivalences.** Each level writes the same report the matching
standalone command writes, so a level already covered today can be reused
instead of re-run:

| Level | Equivalent command | Report |
|-------|--------------------|--------|
| L1 | `/agents:review <path>` | `review/review-[scope]-DATE.md` |
| L2 | — | `architecture/architecture-[scope]-DATE.md` |
| L3 | `/agents:security <path>` | `security/security-[scope]-DATE.md` |
| L4 | — | `sre/sre-reliability-[scope]-DATE.md` |

## Review Target

**Path to review:** $1  
**Options:** $ARGUMENTS

## Quick Reference

- `/review-full src/` — Full 4-level review
- `/review-full src/ --quick` — L1 only (peer review)
- `/review-full src/ --security` — L1 + L3 (peer + security)
- `/review-full src/ --all` — Force all 4 levels

---

## Pre-Review Analysis

Before starting, analyze the target to determine which review levels apply:

<analysis>
# Count source files (adjust extensions as needed for project)
find $1 -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.go" -o -name "*.rs" -o -name "*.java" -o -name "*.rb" -o -name "*.php" \) 2>/dev/null | head -20 | xargs wc -l 2>/dev/null | tail -1 || echo "0 total"
!git diff --stat HEAD~1 -- $1 2>/dev/null | tail -1 || echo "No git history"
</analysis>

<prior_work>
!cat .claude/reports/_registry.md 2>/dev/null | grep -i "review\|security\|arch\|sre" | head -10 || echo "No prior reviews found"
</prior_work>

---

## Review Levels

### Level 1: Peer Review (Always Required)

Invoke the `code-quality` agent with mode=review:

```
Task(code-quality, "
Mode: review
Target: $1

Focus areas:
- Code correctness and logic errors
- Style consistency with project conventions
- Test coverage gaps
- Error handling completeness
- Documentation quality

Severity classification:
- BLOCKING: Must fix before merge
- NON-BLOCKING: Should fix, can defer
- NIT: Nice to have improvements

Output: .claude/reports/review/review-[scope]-YYYY-MM-DD.md
Structure the report as: Summary / Findings / Recommendations.
Give every finding a severity label and a `file:line` location.
")
```

**After completion:** verify and register (see [Post-Review Actions](#post-review-actions))
with `--category review --name "review-[scope]"`.

---

### Level 2: Architecture Review

**Trigger when ANY of these apply:**
- Change exceeds 200 lines
- New API endpoints added
- Database schema modifications
- New services or modules introduced
- Cross-cutting concerns affected

Invoke the `architect` agent with mode=system:

```
Task(architect, "
Mode: system
Target: $1

Context from L1: [Include key findings from peer review]

Assessment criteria:
- Alignment with existing architecture
- Pattern consistency across codebase
- Dependency appropriateness and direction
- API design quality and versioning
- Scalability implications

Use the same severity labels as L1: BLOCKING / NON-BLOCKING / NIT.

Output: .claude/reports/architecture/architecture-[scope]-YYYY-MM-DD.md
Structure the report as: Summary / Findings / Recommendations.
")
```

**After completion:** verify and register with
`--category architecture --name "architecture-[scope]"`.

---

### Level 3: Security Review

**Trigger when change touches ANY of:**
- Authentication or authorization logic
- User input handling or validation
- External API integrations
- Database queries (especially dynamic)
- File system operations
- Cryptographic operations
- Sensitive data (PII, credentials, tokens)

Invoke the `security-engineer` agent with mode=scan:

```
Task(security-engineer, "
Mode: scan
Target: $1

Context from L1/L2: [Include relevant findings]

Security checklist:
- OWASP Top 10 vulnerability scan
- Input validation completeness
- Authentication/authorization weaknesses
- Data exposure risks
- Dependency CVE check

Use the same severity labels as L1: BLOCKING / NON-BLOCKING / NIT.

Output: .claude/reports/security/security-[scope]-YYYY-MM-DD.md
Structure the report as: Summary / Findings / Recommendations.
")
```

**After completion:** verify and register with
`--category security --name "security-[scope]"`.

---

### Level 4: Reliability Review

**Trigger when change affects ANY of:**
- Infrastructure configuration
- Service dependencies
- Error handling or retry logic
- Caching mechanisms
- Database operations at scale
- External service integrations

Invoke the `sre` agent with mode=reliability-review:

```
Task(sre, "
Mode: reliability-review
Target: $1

Context from L1/L2/L3: [Include relevant findings]

Reliability assessment:
- Failure mode identification and handling
- SLO/SLI impact analysis
- Dependency reliability risks
- Graceful degradation capability
- Rollback safety and procedures

Use the same severity labels as L1: BLOCKING / NON-BLOCKING / NIT.

Output: .claude/reports/sre/sre-reliability-[scope]-YYYY-MM-DD.md
Structure the report as: Summary / Findings / Recommendations.
")
```

**After completion:** verify and register with
`--category sre --name "sre-reliability-[scope]"`.

---

## Execution Flow

Based on the `$ARGUMENTS` provided:

1. **`--quick`**: Execute L1 only, skip all other levels
2. **`--security`**: Execute L1 + L3, skip L2 and L4
3. **`--all`**: Execute all four levels regardless of triggers
4. **No flag**: Analyze target and apply triggers automatically

**Sequencing rule (from agent-coordination skill):**  
Each level MAY need prior level's output → Execute sequentially, verify between each.

**Reuse rule.** Because each level writes the same report its standalone
equivalent writes, check `<prior_work>` first: if today's registry already has
the report for this scope and level — e.g. `/agents:review src/` ran an hour
ago and L1 wants `review-src-[today].md` — read that report and feed its
findings forward instead of re-running the agent. Say in the summary which
levels were reused rather than freshly run.

---

## Post-Review Actions

Run these after **each** level completes, before starting the next.

### Verify Deliverables

```bash
SC=.claude/skills/agent-coordination/scripts
uv run --script $SC/verify.py "[category]" "[name]" "[date]"
```

`[name]` is the report stem WITHOUT the date — e.g. `review-src`, not
`review-src-2026-08-03.md`.

### Update Registries

1. **Always:** register the report with `add_report.py`. Do not hand-edit
   `_registry.md` — only this script produces the row format
   `validate_registry.py` accepts:
   ```bash
   uv run --script $SC/add_report.py \
       --category "[category]" --name "[name]" --status Completed \
       --summary "[one-line summary]"
   ```
2. **If issues deferred:** append a row to the **Open** table in
   `.claude/reports/_tech-debt.md`. It is a table, not a checklist — match its
   columns exactly:
   ```
   | TD-NNN | [area] | [description] | [Critical|High|Medium|Low] | YYYY-MM-DD | [source-report].md |
   ```
   Map review severities to the Severity column per the coordination skill:
   BLOCKING → `Critical`/`High`, NON-BLOCKING → `Medium`, NIT → `Low`.
   Get the next ID with:
   ```bash
   grep -oE 'TD-[0-9]+' .claude/reports/_tech-debt.md | sort -t- -k2 -n | tail -1
   ```

---

## Aggregated Summary Report

After completing applicable levels, generate:

```markdown
# Full Review Summary: $1

**Review Date:** YYYY-MM-DD
**Reviewed By:** Claude Code Review System

## Levels Completed
- [x] L1: Peer Review
- [ ] L2: Architecture Review (if applicable)
- [ ] L3: Security Review (if applicable)
- [ ] L4: Reliability Review (if applicable)

## Blocking Issues (Must Fix)
| Level | Issue | Location | Severity |
|-------|-------|----------|----------|
| L1 | [description] | file:line | BLOCKING |

## Non-Blocking Issues (Should Fix)
| Level | Issue | Location | Priority |
|-------|-------|----------|----------|
| L1 | [description] | file:line | HIGH |

## Recommendations
1. [Actionable recommendation]
2. [Actionable recommendation]

## Tech Debt (Deferred)
Items marked "won't fix now" → append to `.claude/reports/_tech-debt.md`

## Verdict
- [ ] **APPROVED**: Ready to merge (all blocking resolved)
- [ ] **CHANGES REQUESTED**: Blocking issues remain

## Report Links
- L1: `.claude/reports/review/review-[scope]-YYYY-MM-DD.md`
- L2: `.claude/reports/architecture/architecture-[scope]-YYYY-MM-DD.md`
- L3: `.claude/reports/security/security-[scope]-YYYY-MM-DD.md`
- L4: `.claude/reports/sre/sre-reliability-[scope]-YYYY-MM-DD.md`
```

**Output:** `.claude/reports/review/review-full-[scope]-YYYY-MM-DD.md`

**Final step:** register the summary too:

```bash
uv run --script $SC/add_report.py --category review \
    --name "review-full-[scope]" --status Completed \
    --summary "Full review of [scope]: [n] blocking, [n] non-blocking"
```

---

## Decision Flowchart

```
┌─────────────────────────────────────────────────────────────┐
│                         START                                │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
              ┌────────────────────────┐
              │   L1: Peer Review      │ ◄── Always runs
              └───────────┬────────────┘
                          ▼
              ┌────────────────────────┐
              │ --quick flag present?  │
              └───────────┬────────────┘
                    │           │
                   Yes          No
                    │           ▼
                    │   ┌──────────────────────────┐
                    │   │ Change > 200 lines OR    │
                    │   │ new API/schema/module?   │
                    │   └───────────┬──────────────┘
                    │         │           │
                    │        Yes          No
                    │         ▼           │
                    │   ┌─────────────┐   │
                    │   │ L2: Arch    │   │
                    │   └──────┬──────┘   │
                    │          ▼          ▼
                    │   ┌──────────────────────────┐
                    │   │ Touches auth/input/data/ │
                    │   │ crypto/external APIs?    │
                    │   └───────────┬──────────────┘
                    │         │           │
                    │        Yes          No
                    │         ▼           │
                    │   ┌─────────────┐   │
                    │   │ L3: Security│   │
                    │   └──────┬──────┘   │
                    │          ▼          ▼
                    │   ┌──────────────────────────┐
                    │   │ Affects infra/deps/      │
                    │   │ error handling/caching?  │
                    │   └───────────┬──────────────┘
                    │         │           │
                    │        Yes          No
                    │         ▼           │
                    │   ┌─────────────┐   │
                    │   │ L4: SRE     │   │
                    │   └──────┬──────┘   │
                    │          │          │
                    ▼          ▼          ▼
              ┌────────────────────────────────┐
              │      Aggregate Results          │
              └───────────────┬────────────────┘
                              ▼
              ┌────────────────────────────────┐
              │   Generate Summary Report       │
              └───────────────┬────────────────┘
                              ▼
              ┌────────────────────────────────┐
              │   Update _registry.md          │
              └────────────────────────────────┘
```
