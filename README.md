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
├── agents/          # 15 specialized agent definitions
├── commands/        # Slash commands for common workflows
├── skills/          # Reusable skill packages
└── reports/         # Generated reports and registries

openspec/            # Spec-driven development (generated per-project, not committed)
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

Install into a target project (copies `.claude/` and bootstraps runtime state):

```bash
./install.sh /path/to/your-project
```

Re-run any time to pull updates — local reports and registries are preserved.
Or copy `.claude/` in manually and run
`bash .claude/skills/agent-coordination/scripts/bootstrap.sh`. The
infrastructure adapts to your project's toolchain automatically. See
[Getting Started](.claude/GETTING_STARTED.md) for details.

## Documentation

See [CLAUDE.md](CLAUDE.md) for AI assistant instructions.
