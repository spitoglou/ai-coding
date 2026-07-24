---
name: Agents: CI
description: Run local CI pipeline (lint, type-check, test, security scan).
category: Agents
tags: [agents, ci, pipeline, quality]
---

**Purpose**
Run a comprehensive local CI pipeline to verify code quality before commits or OpenSpec archiving.

**Project Detection**
First read `.claude/project.md` — if it defines Test/Lint/Type-check/Build
commands (auto-detected block or *Toolchain overrides*), use those verbatim.
Fall back to detecting project type and running the defaults below:

| Config File | Project Type | Lint | Type Check | Test |
|-------------|--------------|------|------------|------|
| `pyproject.toml` | Python | `ruff check .` | `mypy .` | `pytest` |
| `package.json` | Node.js | `npm run lint` | `npm run typecheck` | `npm test` |
| `Cargo.toml` | Rust | `cargo clippy` | (built-in) | `cargo test` |
| `go.mod` | Go | `golangci-lint run` | (built-in) | `go test ./...` |

**Steps**
1. Detect project type from config files in root
2. Run quality checks sequentially using UV for Python projects:

   **Python (pyproject.toml detected):**
   ```bash
   echo "=== Step 1/4: Linting ==="
   uv run ruff check .
   
   echo "=== Step 2/4: Type Checking ==="
   uv run mypy . --ignore-missing-imports
   
   echo "=== Step 3/4: Running Tests ==="
   uv run pytest --tb=short -q
   
   echo "=== Step 4/4: Security Overview ==="
   uv run bandit -r . -q 2>/dev/null || echo "bandit not installed, skipping"
   ```

   **Node.js (package.json detected):**
   ```bash
   echo "=== Step 1/4: Linting ==="
   npm run lint --if-present
   
   echo "=== Step 2/4: Type Checking ==="
   npm run typecheck --if-present
   
   echo "=== Step 3/4: Running Tests ==="
   npm test --if-present
   
   echo "=== Step 4/4: Security Overview ==="
   npm audit --audit-level=moderate 2>/dev/null || true
   ```

   **Toolkit integrity (all project types):**
   ```bash
   echo "=== Step 5/5: Registry integrity ==="
   # Validate the report registry format (no-op-safe if reports/ is empty)
   uv run --script .claude/skills/agent-coordination/scripts/validate_registry.py \
       2>/dev/null || echo "registry validation skipped (no registry yet)"
   ```

3. Report results summary:
   - Lint: Pass/Fail with error count
   - Types: Pass/Fail with error count
   - Tests: Pass/Fail with test count
   - Security: Any obvious issues
   - Registry: Valid/Invalid (format, dates, links)

4. If all pass, output success message.
5. If failures, provide specific remediation steps.

**Quality Gate Criteria**
- [ ] Lint: Zero errors (or within project baseline)
- [ ] Types: No increase from baseline
- [ ] Tests: All pass

**Arguments**
- `$ARGUMENTS` - Optional flags:
  - `--fix` - Auto-fix linting issues (if supported)
  - `--quick` - Skip tests (lint + type-check only)
  - `--python` / `--node` / `--rust` / `--go` - Force specific toolchain

**Example Usage**
```
/agents:ci           # Full CI pipeline (auto-detect)
/agents:ci --fix     # Fix linting issues first
/agents:ci --quick   # Skip tests
/agents:ci --python  # Force Python toolchain
```

**Integration**
- Use before `openspec archive` to ensure quality gate passes
- Use before committing significant changes
- Results can be saved to `.claude/reports/ci/ci-YYYY-MM-DD-HHMM.md` if needed
