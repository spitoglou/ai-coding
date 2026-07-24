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

## Core vs. Project Specifics

The toolkit is a **generic core** you never hand-edit, plus **one file** that
holds everything specific to your project. This lets you update the core in
place without losing your adaptations.

| Layer | Files | On update (`install.py`) |
|-------|-------|--------------------------|
| **Core** (toolkit-owned) | `agents/`, `commands/`, `skills/`, `hooks/`, scripts, `settings.json`, `VERSION` | Overwritten |
| **Specifics** (yours) | `.claude/project.md` | Preserved |
| **Runtime** (generated) | `reports/*`, `settings.local.json` | Preserved |
| **Your additions** | any file you add (e.g. `commands/my-cmd.md`) | Kept (never deleted) |

`.claude/project.md` is where the project's toolchain, architecture,
conventions, and domain live. Core files **reference** it instead of hard-coding
details, so an agent reads project specifics from there. See *Adapting to Your
Project* below.

## Installing into Your Project

This toolkit is designed to be ported into other projects. Two ways:

**From this repo, into a target project:**

```bash
python3 install.py /path/to/your-project        # install or update the core
python3 install.py --check /path/to/your-project  # preview what an update would change
```

This copies the core into the target, bootstraps runtime state, and adapts to
the project (see below). Re-run any time to pull core updates — your
`project.md`, reports, registries, and any files you added are never
overwritten. `--check` shows a file-level preview first: `~` overwritten,
`+` added, `=` your file left untouched.

**Manual copy:** copy `.claude/` into your project, then bootstrap:

```bash
python3 .claude/skills/agent-coordination/scripts/bootstrap.py
```

Bootstrap is idempotent — it seeds `_registry.md`/`_tech-debt.md` from their
templates, creates the report category directories, and runs `adapt.py`. The
installed core version is recorded in `.claude/VERSION`.

## Adapting to Your Project

Two passes keep `.claude/project.md` current:

1. **Deterministic** — `adapt.py` detects the toolchain (test/lint/type-check/
   build commands, package manager, project name) and (re)writes the managed
   `CORE:AUTODETECT` block. It runs automatically during bootstrap and every
   session, and is safe to run by hand:

   ```bash
   python3 .claude/skills/agent-coordination/scripts/adapt.py
   ```

2. **Judgement-based** — the `/adapt` command has an agent read the repo and
   fill in the free-form **Project-specific notes** (architecture, conventions,
   domain). Run it once after install, and again (`/adapt --refresh`) when the
   project changes.

Only the managed block is regenerated; your notes below it are always preserved.
If an auto-detected command is wrong, record the correct one under *Toolchain
overrides* in `project.md` — it takes precedence.

## Self-Healing (SessionStart Hook)

`.claude/settings.json` registers a `SessionStart` hook
(`.claude/hooks/session_start.py`) that runs `bootstrap.py` at the start of
every Claude Code session. This keeps the runtime state (registries, report
directories) present even if `reports/` was cleaned or the toolkit was just
ported in — no manual bootstrap needed. It's idempotent and never blocks the
session. To disable, remove the `SessionStart` entry from `.claude/settings.json`.

All infrastructure scripts are Python (cross-platform: Linux, macOS, Windows) —
there are no shell scripts to maintain. The hook invokes `python3`; on a native
Windows shell where the interpreter is `python`, change the one command in
`settings.json` accordingly (Git Bash / WSL already provide `python3`).

## Registry Workflow

Report entries are managed with helper scripts so the registry stays in the one
format the tooling expects (avoid hand-editing `_registry.md`):

```bash
SC=.claude/skills/agent-coordination/scripts

# Record a completed report (--name is the stem WITHOUT the date)
uv run $SC/add_report.py --category review --name review-src \
    --status Completed --summary "Peer review of src/" --scaffold

# Lint the registry (run by /agents:ci): bad rows, dates, links, missing files
uv run $SC/validate_registry.py
```

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
