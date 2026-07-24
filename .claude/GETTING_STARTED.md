# Getting Started with AI Coding Infrastructure

This guide introduces the three core subsystems and walks you through your first workflow.

## System Overview

### 1. Agent Coordination

Located in `.claude/skills/agent-coordination/`, this system orchestrates specialized AI agents:

- **15 Agents** - Each with specific expertise (code-quality, security-engineer, architect, etc.)
- **Registry** - Tracks all completed work in `_registry.md`
- **Tech Debt** - Tracks deferred improvements in `_tech-debt.md`
- **Reports** - Organized by category in `.claude/reports/`

### 2. Design System

Located in `.claude/skills/design/`, provides consistent UI/UX:

- **Brand Colors** - For UI elements (buttons, cards, navigation)
- **Data Colors** - For visualizations (charts, graphs, metrics)
- **Components** - Pre-defined patterns for buttons, cards, data displays

### 3. OpenSpec

Located in `openspec/`, enables spec-driven development:

- **Specs** - Define what IS built (`openspec/specs/`)
- **Changes** - Propose what SHOULD change (`openspec/changes/`)
- **Workflow** - Proposal → Implementation → Archive

> **Note:** `openspec/` is **not committed** with this toolkit — it's
> git-ignored and generated per-project. If it's missing, initialize it in your
> project root with `npx openspec init` (or `openspec init`). Until then, the
> OpenSpec commands and the `openspec/AGENTS.md` references below are inactive.

## Your First Workflow: Code Review

Run a code review using the code-quality agent:

```
/agents:review .
```

This will:
1. Invoke the code-quality agent in review mode
2. Analyze the specified files
3. Generate a report in `.claude/reports/review/`
4. Update the registry

## Understanding Reports

Reports are the knowledge transfer mechanism. Each report includes:

- **Header** - Agent, date, status, scope
- **Findings** - Organized by severity
- **Recommendations** - Actionable next steps

Browse existing reports:
```bash
ls .claude/reports/
cat .claude/reports/_registry.md
```

## Working with OpenSpec

When making significant changes:

1. **Check existing specs**: `openspec list --specs`
2. **Check active changes**: `openspec list`
3. **Create proposal**: `/openspec:proposal`
4. **After approval**: `/openspec:apply`
5. **After deployment**: `/openspec:archive`

## Installing into Your Project

This toolkit is designed to be ported into other projects. Two ways:

**From this repo, into a target project:**

```bash
./install.sh /path/to/your-project
```

This copies `.claude/` into the target and bootstraps its runtime state.
Re-run any time to pull toolkit updates — your local reports and registries
(`_registry.md`, `_tech-debt.md`) are never overwritten.

**Manual copy:** copy `.claude/` into your project, then bootstrap the runtime
registries and report directories:

```bash
bash .claude/skills/agent-coordination/scripts/bootstrap.sh
```

Bootstrap is idempotent — it seeds `_registry.md` and `_tech-debt.md` from
their templates (leaving existing ones untouched) and creates the report
category directories the commands expect. The installed toolkit version is
recorded in `.claude/VERSION`.

## Customization

- **Agent model:** each agent pins a default model in its frontmatter
  (`model: sonnet` in `.claude/agents/*.md`). Change that field to point an
  agent at a different model for your project.
- **Report categories:** add directories under `.claude/reports/` and a
  matching section in `_registry-template.md` to track new report types.

## Next Steps

- Explore agent definitions in `.claude/agents/`
- Try `/review-full` for comprehensive multi-level review
- Read the design system in `.claude/skills/design/SKILL.md`
- Check OpenSpec documentation in `openspec/AGENTS.md`

## Common Commands

| Command | Description |
|---------|-------------|
| `/agents:review [path]` | Code review |
| `/agents:security [path]` | Security scan |
| `/agents:coverage` | Test coverage |
| `/agents:ci` | Run CI pipeline (auto-detects project type) |
| `/test` | Run tests (auto-detects test runner) |
| `/release` | Version bump and release |
| `/rfc` | Create design document |
| `/debt` | View tech debt |
| `/archive` | Archive old reports |

## Project Type Support

The infrastructure auto-detects project type from config files:

| Config File | Project Type |
|-------------|--------------|
| `pyproject.toml` | Python (uses UV) |
| `package.json` | Node.js |
| `Cargo.toml` | Rust |
| `go.mod` | Go |

Scripts and commands adapt automatically to your project's toolchain.
