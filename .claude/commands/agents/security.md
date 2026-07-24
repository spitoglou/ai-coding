---
name: Agents: Security
description: Invoke security-engineer agent for security vulnerability scan.
category: Agents
tags: [agents, security, vulnerability, owasp]
---

**Purpose**
Run a security vulnerability assessment using the security-engineer agent.

**Steps**
1. Check `.claude/reports/_registry.md` for recent security scans.
2. Determine scope from user input (specific files, directories, or full codebase).
3. Invoke the security-engineer agent in scan mode:
   ```
   Task(security-engineer, "
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
   
   **Output:**
   - Report: .claude/reports/security/security-scan-YYYY-MM-DD.md
   
   **Mode:** scan
   ")
   ```
4. Verify report was created using `verify.py`.
5. Update `_registry.md` with the new report.
6. For critical/high vulnerabilities:
   - Check if OpenSpec proposal exists
   - Create tech debt entries if not immediately addressed
   - Consider creating OpenSpec proposal for significant fixes

**Arguments**
- `$ARGUMENTS` - Optional: specific files, directories, or focus area (defaults to full codebase)

**Example Usage**
```
/agents:security                    # Scan full codebase
/agents:security lib/ api/          # Scan specific directories
/agents:security --focus auth       # Focus on authentication
```

**Integration**
- Links to OpenSpec: Security fixes often need formal proposals
- Links to Tech Debt: All findings should be tracked in `_tech-debt.md`
