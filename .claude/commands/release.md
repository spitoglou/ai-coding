---
description: Execute the release procedure (version bump, changelog, tag) for this project.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Release Procedure

Execute the release procedure using version management tools appropriate for the project.

## Project Detection

| Config File | Version Tool | Lock File |
|-------------|--------------|-----------|
| `pyproject.toml` | `uv run cz bump` | `uv.lock` |
| `package.json` | `npm version` or `standard-version` | `package-lock.json` |
| `Cargo.toml` | `cargo release` | `Cargo.lock` |

## 1. Pre-Release Checks

Verify the working tree is clean and tests pass:
```bash
git status
# Run project-appropriate test command (see /test)
```

Review commits since last release:
```bash
git log --oneline $(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD)..HEAD
```

## 2. Bump Version

### Python (with commitizen + UV)

```bash
# Auto-determine bump from conventional commits
uv run cz bump --changelog

# Or specify explicitly
uv run cz bump --changelog --increment PATCH|MINOR|MAJOR

# Sync lock file
uv sync --all-extras
git add uv.lock
git commit --amend --no-edit
```

### Node.js

```bash
# Using npm
npm version patch|minor|major

# Or with standard-version (conventional commits)
npx standard-version
```

### Rust

```bash
cargo release patch|minor|major
```

## 3. Push Release

Push commit and tags to remote:
```bash
git push && git push --tags
```

## 4. Verify

Confirm the release:
```bash
# Check latest tags
git tag -l "v*" | tail -5

# Check changelog
head -50 CHANGELOG.md
```

## Dry Run

Preview changes without committing:

**Python:** `uv run cz bump --dry-run`
**Node.js:** `npx standard-version --dry-run`

## Configuration Examples

**Python (pyproject.toml):**
```toml
[tool.commitizen]
name = "cz_conventional_commits"
version_provider = "pep621"
tag_format = "v$version"
update_changelog_on_bump = true
```

**Node.js (package.json):**
```json
{
  "standard-version": {
    "tag-prefix": "v"
  }
}
```
