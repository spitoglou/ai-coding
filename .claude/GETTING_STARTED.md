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
