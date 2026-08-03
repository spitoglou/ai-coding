---
description: Run tests with test-engineer agent
allowed-tools: Bash
argument-hint: "[test suite or path]"
---

# Run Tests

## Project Detection

Detect test runner from project config:

| Config File | Test Command |
|-------------|--------------|
| `pyproject.toml` | `uv run pytest` |
| `package.json` | `npm test` |
| `Cargo.toml` | `cargo test` |
| `go.mod` | `go test ./...` |

## Process

1. **Detect:** Identify project type from config files
2. **Scope:** Use argument for specific suite/path, or run full suite
3. **Execute:** Run appropriate test command with UV wrapper for Python
4. **Report:** Results + coverage in `.claude/reports/tests/`

## Arguments

- `unit` - Unit tests only
- `integration` - Integration tests
- `e2e` - End-to-end tests
- `[path]` - Specific file/directory/pattern
- None - Full test suite

## Examples

```bash
/test                       # All tests (auto-detect runner)
/test unit                  # Unit tests
/test tests/                # Specific directory
/test test_auth             # Pattern match
```

## Test Commands by Project Type

**Python:**
```bash
uv run pytest                           # Full suite
uv run pytest tests/unit/               # Unit tests
uv run pytest -k "test_auth"            # Pattern match
uv run pytest --cov=. --cov-report=term # With coverage
```

**Node.js:**
```bash
npm test                    # Full suite
npm test -- --grep "auth"   # Pattern match
npm run test:unit           # If script exists
```

**Rust:**
```bash
cargo test                  # Full suite
cargo test auth             # Pattern match
cargo test --lib            # Library tests only
```

**Go:**
```bash
go test ./...               # Full suite
go test ./pkg/auth/...      # Specific package
go test -v -run TestAuth    # Pattern match
```
