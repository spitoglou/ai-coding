---
description: Invoke security-engineer agent for security vulnerability scan.
argument-hint: "[path...] [--focus <area>]"
allowed-tools: Read, Glob, Grep, Bash, Task
---

**Purpose**
Run a security vulnerability assessment using the security-engineer agent.

This is L3 of `/review-full` run on its own — same agent, same mode, same
report contract.

**Before proceeding:** Read the `agent-coordination` skill at
`.claude/skills/agent-coordination/SKILL.md` for the report naming convention,
severity vocabulary, and registry helpers this command depends on.

**Steps**
1. Check `.claude/reports/_registry.md` for recent security scans of the same scope.
2. Determine scope from user input (specific files, directories, or full
   codebase) and derive the scope slug per the skill's Report Naming rules.
3. Invoke the security-engineer agent in scan mode:
   ```
   Task(security-engineer, "
   **Mode:** scan

   **Objective:** Security vulnerability assessment focusing on OWASP Top 10.

   **Scope:** [specified files/directories or full codebase]

   **Focus Areas:**
   - Authentication and session management
   - Input validation and injection prevention
   - Access control and authorization
   - Data protection and encryption
   - Security headers and configurations

   **Context from prior work:**
   - [Reference any relevant recent reports from registry]

   **Severity classification** (use these exact labels):
   - BLOCKING: Must fix before merge
   - NON-BLOCKING: Should fix, can defer
   - NIT: Nice to have

   **Output:** .claude/reports/security/security-[scope]-YYYY-MM-DD.md
   Structure the report as: Summary / Findings / Recommendations.
   Give every finding a severity label and a `file:line` location.
   ")
   ```
4. Verify the report was created:
   ```bash
   uv run --script .claude/skills/agent-coordination/scripts/verify.py \
       security "security-[scope]" "YYYY-MM-DD"
   ```
5. Register it (do not hand-edit `_registry.md`):
   ```bash
   uv run --script .claude/skills/agent-coordination/scripts/add_report.py \
       --category security --name "security-[scope]" --status Completed \
       --summary "Security scan of [scope]"
   ```
6. For BLOCKING vulnerabilities:
   - Check if OpenSpec proposal exists
   - Create tech debt entries if not immediately addressed
   - Consider creating OpenSpec proposal for significant fixes

**Arguments**
- `$ARGUMENTS` - Optional: specific files, directories, or focus area (defaults to full codebase)

**Example Usage**
```
/agents:security                    # Scan full codebase   → security-all-DATE.md
/agents:security lib/ api/          # Scan specific dirs   → security-lib-api-DATE.md
/agents:security --focus auth       # Focus on auth        → security-all-auth-DATE.md
```

**Integration**
- Links to OpenSpec: Security fixes often need formal proposals
- Links to Tech Debt: All findings should be tracked in `_tech-debt.md` as table
  rows — see the coordination skill's Finding Severity mapping
- Escalation: `/review-full [scope] --security` runs this as its L3 alongside
  peer review, reusing this exact report if it already ran today
