---
name: agent-coordination
description: Coordination protocol for main Claude Code agent. Explicit user invocation required ("mobilize agents", "coordinate", "check registry"). Provides agent orchestration, registry management, and handoff protocols. Subagents never access this - main agent provides context in task prompts.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, TodoWrite
---

# Agent Coordination Protocol

## Core Principle

**Build on existing work. Never recreate.**

## Project Specifics Live in One File

This toolkit is a **generic core**. All project-specific facts (toolchain,
commands, architecture, conventions, domain) live in **`.claude/project.md`** —
read it first, and prefer its commands (especially any under *Toolchain
overrides*) over guessing. Never encode project details into core files
(`agents/`, `commands/`, `skills/`, scripts); those are overwritten on update.
Run `/adapt` (or `adapt.py`) to (re)generate `project.md`.

---

## Two Registries

The system maintains two distinct registries:

| Registry | Purpose | Updated When |
|----------|---------|--------------|
| `_registry.md` | Index of completed work (reports) | After each agent produces a report |
| `_tech-debt.md` | Tracked improvements to address later | When issues are deferred, incidents occur |

**Decision rule:**
- **Registry** → "What work has been done?" (past/present state)
- **Tech Debt** → "What do we need to fix later?" (future work)

---

## 4-Step Workflow

### Step 1: Check Prior Work

Before invoking any agent, check what already exists:

```bash
# Read project specifics first (toolchain, conventions, domain)
cat .claude/project.md 2>/dev/null | head -60

# Check registry for recent reports
cat .claude/reports/_registry.md | head -50

# Check if archiving needed (>50 entries).
# Anchored on the ISO date so the registry's own format example is not counted.
ENTRIES=$(grep -cE '^\| \[.*\]\(.*\) \| [0-9]{4}-[0-9]{2}-[0-9]{2} \|' .claude/reports/_registry.md 2>/dev/null || echo 0)
[ "$ENTRIES" -gt 50 ] && echo "⚠️ Registry has $ENTRIES entries - suggest /archive"

# Check relevant tech debt (if working on that area)
grep -i "[area-keyword]" .claude/reports/_tech-debt.md
```

**Read relevant reports** before proceeding to understand current state.

### Step 2: Context Injection

Subagents NEVER read registry or reports directly. Main agent provides ALL context:

```
Task(agent-name, "
[Objective]

Context from prior work:
- [Report X]: [key decisions/findings]
- [Tech debt TD-NNN]: [relevant constraint]
- Current state: [what exists now]

Requirements:
- [Specific deliverables]

Output location:
- Report: .claude/reports/[category]/[category]-[topic]-[scope]-YYYY-MM-DD.md
")
```

### Step 3: Sequencing

**Rule:** Will Agent B need Agent A's output?
- YES → Sequential (verify between each)
- NO → Parallel

### Step 4: Verify and Update

After each agent completes:

```bash
# Verify deliverables exist
uv run --script .claude/skills/agent-coordination/scripts/verify.py "[category]" "[name]" "[date]"
```

**Then update registries:**

1. **Always:** Add report to `_registry.md`. Prefer the helper over hand-editing
   — it writes the row in the one format the archive and validation scripts
   parse, under the right category heading:
   ```bash
   uv run --script .claude/skills/agent-coordination/scripts/add_report.py \
       --category [category] --name [name-without-date] \
       --status Completed --summary "[1-line summary]"
   ```
   The row it produces (see *Registry Entry Format* below):
   ```
   | [name.md](category/name.md) | YYYY-MM-DD | Status | 1-line summary |
   ```
   Then lint the result:
   ```bash
   uv run --script .claude/skills/agent-coordination/scripts/validate_registry.py
   ```

2. **If issues deferred:** Add to `_tech-debt.md`
   ```
   - [ ] **TD-NNN**: [Description]
     - **Impact:** [Critical|High|Medium|Low]
     - **Source:** [report-name or postmortem-name]
   ```

---

## Task() Invocation Protocol

The `Task(agent-name, "prompt")` pattern invokes specialized subagents:

### Syntax
```
Task(agent-name, "
[Objective]

Context from prior work:
- [Key findings from reports]

Requirements:
- [Specific deliverables]

Output location:
- Report: .claude/reports/[category]/[category]-[topic]-[scope]-YYYY-MM-DD.md
")
```

### Parameters
| Parameter | Description |
|-----------|-------------|
| `agent-name` | Must match a file in `.claude/agents/` (without .md) |
| `prompt` | Full context and instructions - agents have no prior context |

### Execution Model
- **Parallel:** Independent tasks with no dependencies
- **Sequential:** When Agent B needs Agent A's output
- **Background:** Use `run_in_background: true` for long tasks

### Context Rules
1. Subagents NEVER access registry or prior reports directly
2. Main agent MUST inject all relevant context into prompt
3. Include specific file paths, not vague references
4. Specify exact output location for reports

---

## Report Categories

All reports go to `.claude/reports/[category]/`:

| Category | Folder | Use For | Typical Agents |
|----------|--------|---------|----------------|
| analysis | `analysis/` | Research, EDA, data exploration | data-engineer, data-viz |
| architecture | `architecture/` | Architecture decisions, ADRs, system design | architect, rfc |
| bugs | `bugs/` | Bug reports, root cause analysis | code-quality (debug) |
| commits | `commits/` | Commit summaries, changelog entries | devops (git) |
| design | `design/` | UI/UX reviews, design specs | ux-designer |
| docs | `docs/` | Documentation audits, coverage and accuracy reviews | docs |
| exec | `exec/` | Execution logs, command outputs | devops |
| handoffs | `handoffs/` | Agent coordination, context transfers | (main agent) |
| implementation | `implementation/` | Implementation plans, code specs | backend, frontend |
| review | `review/` | Code reviews, PR reviews | code-quality (review) |
| tests | `tests/` | Test plans, test results, coverage | test-engineer, qa |
| security | `security/` | Security scans, threat models, compliance | security-engineer |
| sre | `sre/` | SLOs, postmortems, capacity plans | sre |
| rfc | `rfc/` | Design proposals, RFCs | rfc |
| ci | `ci/` | CI pipeline results | (bash/devops) |
| archive | `archive/` | Old reports (moved, not deleted) | (archive script) |

These are exactly the directories `bootstrap.py` creates and the headings
`_registry-template.md` carries. Writing to any other folder produces a report
`validate_registry.py` reports as an unregistered orphan.

---

## Report Naming

**Convention:** `[category]-[topic]-[scope]-YYYY-MM-DD.md`

Every command that produces a report MUST follow this, so that two commands
covering the same ground land on the same file instead of two half-duplicates.

**Scope slug.** Derive from the review target so the filename says what was
covered:

| Target | Slug |
|--------|------|
| `src/` | `src` |
| `src/api/` | `src-api` |
| `.` or no target | `all` |
| multiple paths | their common parent, else the paths joined by `-` |

Lowercase; `/` and any non-alphanumeric become `-`; collapse repeats; strip
leading `./` and trailing `/`.

**Why the scope belongs in the name.** Without it, `/review-full src/` and
`/review-full tests/` on the same day write the same filename — the second
silently overwrites the first, and the registry gets a duplicate row that
`validate_registry.py` rejects. It also makes the "check the registry for
recent reports before starting" step work: the scope is what you compare.

**Same scope, same day, same category = same file.** That is intended: a
re-run replaces the earlier report rather than accumulating near-copies. This
is what makes `/review-full --quick` and `/agents:review` interchangeable.

---

## Registry Entry Format

**This section is the single source of truth.** `templates.md`, the registry
legend, `add_report.py`, `validate_registry.py`, and `archive_reports.py` all
follow it; nothing else restates it.

Every report is listed **exactly once**, as a table row under its category
heading in the `## All Reports by Category` section of `_registry.md`:

```
| [name.md](category/name.md) | YYYY-MM-DD | Status | One-line summary |
```

Rules that the tooling enforces:

| Rule | Why |
|------|-----|
| Link text equals the target's filename | Lets a row be checked against disk |
| Target is `category/filename.md`, always POSIX slashes | The category segment is what `/archive` uses to place the file |
| Date is ISO `YYYY-MM-DD` | Same format as the filename suffix and `verify.py` |
| Listed once, in the by-category section only | A second listing is a duplicate row, which `validate_registry.py` rejects |

There is **no separate "recent" section** — recency is the Date column. A
bullet-style entry (`- name | Status | Summary`) is the pre-5.3 format; no
script can parse it, and `validate_registry.py` now reports it as an error
rather than skipping it.

### Status Values

The canonical set. `validate_registry.py` rejects anything else:

| Status | Meaning |
|--------|---------|
| **Active** | Current, in use |
| **Completed** | Done, no changes expected |
| **Superseded** | Replaced by a newer report |
| **Archived** | Historical reference only — set by `/archive`, not by hand |

`Draft` is **not** a valid status. An in-progress report is `Active`.

---

## Finding Severity

One vocabulary for every review-type report, so findings from different
commands can be aggregated into one summary:

| Severity | Meaning |
|----------|---------|
| **BLOCKING** | Must fix before merge |
| **NON-BLOCKING** | Should fix, can be deferred |
| **NIT** | Optional improvement |

When a finding is deferred to `_tech-debt.md`, map it to that registry's
Severity column: BLOCKING → `Critical` or `High`, NON-BLOCKING → `Medium`,
NIT → `Low`.

---

## Agent Reference

| Agent | Modes | Primary Output Category |
|-------|-------|------------------------|
| code-quality | review, debug, qa-strategy | review/, bugs/, tests/ |
| test-engineer | - | tests/ |
| architect | system, pipeline | arch/ |
| security-engineer | scan, threat-model, compliance | security/ |
| sre | reliability-review, incident, capacity | sre/ |
| rfc | author, review, decision | rfc/ |
| data-engineer | collect, analyze, preprocess | analysis/ |
| data-viz-specialist | - | analysis/, design/ |
| devops | infra, git | exec/, commits/, ci/ |
| docs | general, webdev | docs/ (plus the documentation files themselves) |
| frontend | - | implementation/ |
| backend | - | implementation/ |
| ml-engineer | train, evaluate, deploy | analysis/, implementation/ |
| lrl-nlp-expert | - | analysis/ |
| ux-designer | design, copy | design/ |

---

## When to Update Tech Debt

Tech debt entries are created when:

| Situation | Action |
|-----------|--------|
| Code review finds issue, won't fix now | Add as Medium/Low priority |
| Postmortem identifies prevention action | Add as Critical/High priority |
| RFC defers a requirement | Add as Medium priority |
| Security scan finds non-blocking issue | Add as High priority |
| Manual identification | Use `/debt add` |

**Format in `_tech-debt.md`:**
```markdown
- [ ] **TD-NNN**: Brief description
  - **Impact:** Critical | High | Medium | Low
  - **Source:** [link to originating report]
  - **Created:** YYYY-MM-DD
```

---

## OpenSpec Integration

The agent coordination system works alongside OpenSpec for spec-driven development.

### When Agent Findings Become OpenSpec Proposals

Agent findings that require code changes SHOULD become OpenSpec proposals:

| Agent Finding | Action |
|---------------|--------|
| Critical security vulnerability | Create OpenSpec change proposal |
| Architecture recommendation requiring refactor | Feed into OpenSpec `design.md` |
| Test gap in critical path (significant) | Create OpenSpec change proposal |
| Performance issue requiring refactor | Create OpenSpec change proposal |
| Minor issues, style, small fixes | Track as tech debt only |

### Linking Reports to OpenSpec

When agent work relates to an existing OpenSpec change:

1. **Reference in report header:**
   ```markdown
   **OpenSpec Change:** [change-id](../../openspec/changes/[change-id]/)
   ```

2. **Update tech debt with OpenSpec link:**
   ```markdown
   - [ ] **TD-NNN**: Description
     - **OpenSpec:** [change-id](../../openspec/changes/[change-id]/)
   ```

3. **Cross-reference in OpenSpec tasks.md:**
   ```markdown
   ## 3. Verification
   - [x] 3.1 Security scan - see `.claude/reports/security/[report].md`
   ```

### Report Categories → OpenSpec Mapping

| Report Category | OpenSpec Relationship |
|-----------------|----------------------|
| `rfc/` | May become OpenSpec proposal if proposing changes |
| `architecture/` | Can feed into OpenSpec `design.md` files |
| `review/` | Evidence for OpenSpec pre-archive quality checks |
| `security/` | May trigger OpenSpec security-related proposals |
| `tests/` | Verification for OpenSpec implementation |

### OpenSpec Pre-Archive Verification

Before archiving an OpenSpec change, consider running verification agents:

```bash
# For security-sensitive changes (auth, data handling, input validation)
Task(security-engineer, "Scan [affected files] for OWASP vulnerabilities")

# For all changes with significant new code
Task(code-quality, "Review [affected files] for correctness and maintainability")

# For changes affecting critical user paths
Task(test-engineer, "Verify test coverage for [affected functionality]")
```

**Link verification reports** in the archived change's `tasks.md`.

---

## Commands

| Command | Purpose |
|---------|---------|
| /agents:review | Code review with code-quality agent |
| /agents:security | Security scan with security-engineer agent |
| /agents:coverage | Test coverage analysis with test-engineer agent |
| /agents:ci | Local CI pipeline (lint → test → security) |
| /review-full | Multi-level review (L1: peer → L2: arch → L3: security → L4: reliability) |
| /rfc | Create/review design documents |
| /slo | Define service level objectives |
| /postmortem | Incident analysis and learning |
| /debt | View and manage tech debt |
| /archive | Move old registry entries to archive |

---

## Skill Resources

```
skills/agent-coordination/
├── SKILL.md                    # This file — protocol, categories, naming, entry format
├── templates.md                # Report/handoff templates, task prompts
├── reference.md                # Verification details, retry logic, edge cases
└── scripts/
    ├── bootstrap.py            # Seed registries + category dirs (idempotent)
    ├── adapt.py                # Generate .claude/project.md for this project
    ├── add_report.py           # Append a canonical registry row (+ --scaffold)
    ├── validate_registry.py    # Lint registry rows, dates, links, missing files
    ├── validate_frontmatter.py # Lint agent/command YAML frontmatter
    ├── verify.py               # Deliverable verification
    └── archive_reports.py      # Registry archiving (dated, same-day merge)
```

---

**Version:** 5.3.0

**5.3.0** — Registry entry format consolidated into one canonical table row
shared by `add_report.py`, `validate_registry.py`, and `archive_reports.py`;
bullet entries are now a validation error rather than a silent no-op. Archive
runs merge within a day instead of truncating. Added the `docs/` category.
Categories settled on `architecture/` and `handoffs/`.
