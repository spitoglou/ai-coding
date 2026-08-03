---
description: Invoke code-quality agent for code review of specified scope.
argument-hint: <path> [path...]
allowed-tools: Read, Glob, Grep, Bash, Task
---

**Purpose**
Run a code review using the code-quality agent on specified files or directories.

This is L1 of `/review-full` run on its own — same agent, same mode, same
report contract. `/review-full <path> --quick` is equivalent.

**Before proceeding:** Read the `agent-coordination` skill at
`.claude/skills/agent-coordination/SKILL.md` for the report naming convention,
severity vocabulary, and registry helpers this command depends on.

**Steps**
1. Check `.claude/reports/_registry.md` for recent reviews of the same scope to
   avoid duplication.
2. Determine scope from user input (specific files, directories, or current
   directory) and derive the scope slug per the skill's Report Naming rules.
3. Invoke the code-quality agent in review mode:
   ```
   Task(code-quality, "
   **Mode:** review

   **Objective:** Code review focusing on security, correctness, performance, maintainability.

   **Scope:** [specified files/directories]

   **Context from prior work:**
   - [Reference any relevant recent reports from registry]

   **Severity classification** (use these exact labels):
   - BLOCKING: Must fix before merge
   - NON-BLOCKING: Should fix, can defer
   - NIT: Nice to have

   **Output:** .claude/reports/review/review-[scope]-YYYY-MM-DD.md
   Structure the report as: Summary / Findings / Recommendations.
   Give every finding a severity label and a `file:line` location.
   ")
   ```
4. Verify the report was created:
   ```bash
   uv run --script .claude/skills/agent-coordination/scripts/verify.py \
       review "review-[scope]" "YYYY-MM-DD"
   ```
5. Register it (do not hand-edit `_registry.md`):
   ```bash
   uv run --script .claude/skills/agent-coordination/scripts/add_report.py \
       --category review --name "review-[scope]" --status Completed \
       --summary "Peer review of [scope]"
   ```
6. If BLOCKING issues are found, consider creating an OpenSpec proposal. Deferred
   findings go to `_tech-debt.md` as table rows — see the skill's Finding
   Severity mapping.

**Arguments**
- `$ARGUMENTS` - Files or directories to review (required)

**Example Usage**
```
/agents:review .                    # Review current directory  → review-all-DATE.md
/agents:review lib/                 # Review lib directory      → review-lib-DATE.md
/agents:review api/ services/       # Review multiple dirs      → review-api-services-DATE.md
/agents:review auth.py session.py   # Review specific files     → review-auth-session-DATE.md
```

**Integration**
- Links to OpenSpec: If review identifies issues requiring changes, reference in OpenSpec proposals
- Links to Tech Debt: Add findings to `_tech-debt.md` if not immediately addressed
- Escalation: for anything beyond peer review (architecture, security, or
  reliability), run `/review-full [scope]`. It reuses this exact report as its
  L1 and adds the levels its triggers select, so nothing is reviewed twice.
