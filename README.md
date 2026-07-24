# AI Coding Infrastructure

Reusable Claude Code infrastructure with agent coordination, design system, and OpenSpec integration. Project-agnostic and works with any language/framework.

## Quick Start

- [Getting Started](.claude/GETTING_STARTED.md)
- [Agent Coordination](.claude/skills/agent-coordination/SKILL.md)
- [Design System](.claude/skills/design/SKILL.md)
- OpenSpec Guide — `openspec/AGENTS.md` (generated locally, see note below)

## Structure

```
.claude/
├── agents/               # 15 specialized agent definitions   ┐
├── commands/             # Slash commands for common workflows │ generic core
├── skills/               # Reusable skill packages             │ (updated in place)
├── hooks/                # SessionStart self-heal hook         ┘
├── project-template.md   # Template for the project profile (core)
├── project.md            # YOUR project specifics (preserved on update)
└── reports/              # Generated reports and registries (preserved)

openspec/                 # Spec-driven development (generated per-project, not committed)
```

> **Note on OpenSpec:** the `openspec/` directory (and its `AGENTS.md`) is
> **not committed** — it's intentionally git-ignored and generated per-project
> by the [OpenSpec CLI](https://github.com/Fission-AI/OpenSpec). If it's absent
> after porting this toolkit in, initialize it in your project root:
>
> ```bash
> npx openspec init   # or: openspec init
> ```
>
> The OpenSpec references throughout these docs and `CLAUDE.md` activate once
> that directory exists.

## Key Commands

| Command | Purpose |
|---------|---------|
| `/adapt` | Adapt the core to this project (`project.md`) |
| `/agents:review [path]` | Code review |
| `/agents:security [path]` | Security scan |
| `/agents:coverage` | Test coverage analysis |
| `/agents:ci` | CI pipeline (lint, type-check, test) |
| `/test` | Run tests (auto-detects runner) |
| `/release` | Version bump and release |
| `/rfc` | Create/review design documents |
| `/review-full [path]` | Multi-level review |

## Project Type Support

Commands auto-detect project type from config files:

| Config File | Project Type |
|-------------|--------------|
| `pyproject.toml` | Python (uses UV) |
| `package.json` | Node.js |
| `Cargo.toml` | Rust |
| `go.mod` | Go |

## Requirements

- [UV](https://docs.astral.sh/uv/) - For running infrastructure scripts
- Claude Code CLI - For agent execution

## Usage

Install into a target project (copies the core, bootstraps runtime state, and
adapts to the project):

```bash
uv run --script install.py /path/to/your-project          # install or update
uv run --script install.py --check /path/to/your-project  # preview an update, change nothing
```

The toolkit is a **generic core** plus one project-specific file,
`.claude/project.md`. Re-run `install.py` any time to pull core updates — your
`project.md`, reports, registries, and any files you added are never
overwritten. Run `/adapt` (or `adapt.py`) to (re)generate `project.md` for your
project's toolchain and conventions. See
[Getting Started](.claude/GETTING_STARTED.md) for the full model.

## Documentation

See [CLAUDE.md](CLAUDE.md) for AI assistant instructions.
