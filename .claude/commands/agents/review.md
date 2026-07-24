---
name: Agents: Review
description: Invoke code-quality agent for code review of specified scope.
category: Agents
tags: [agents, review, code-quality]
---

**Purpose**
Run a code review using the code-quality agent on specified files or directories.

**Steps**
1. Check `.claude/reports/_registry.md` for recent reviews to avoid duplication.
2. Determine scope from user input (specific files, directories, or current directory).
3. Invoke the code-quality agent in review mode:
   ```
   Task(code-quality, "
   **Objective:** Code review focusing on security, correctness, performance, maintainability.
   
   **Scope:** [specified files/directories]
   
   **Context from prior work:**
   - [Reference any relevant recent reports from registry]
   
   **Output:**
   - Report: .claude/reports/review/review-[scope]-YYYY-MM-DD.md
   
   **Mode:** review
   ")
   ```
4. Verify report was created using `verify.py`.
5. Update `_registry.md` with the new report.
6. If critical issues found, consider creating OpenSpec proposal or tech debt entries.

**Arguments**
- `$ARGUMENTS` - Files or directories to review (required)

**Example Usage**
```
/agents:review .                    # Review current directory
/agents:review lib/                 # Review lib directory
/agents:review api/ services/       # Review multiple directories
/agents:review auth.py session.py   # Review specific files
```

**Integration**
- Links to OpenSpec: If review identifies issues requiring changes, reference in OpenSpec proposals
- Links to Tech Debt: Add findings to `_tech-debt.md` if not immediately addressed
