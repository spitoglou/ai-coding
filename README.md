# AI Coding Infrastructure

Reusable Claude Code infrastructure with agent coordination, design system, and OpenSpec integration. Project-agnostic and works with any language/framework.

## Quick Start

- [Getting Started](.claude/GETTING_STARTED.md)
- [Agent Coordination](.claude/skills/agent-coordination/SKILL.md)
- [Design System](.claude/skills/design/SKILL.md)
- [OpenSpec Guide](openspec/AGENTS.md)

## Structure

```
.claude/
├── agents/          # 15 specialized agent definitions
├── commands/        # Slash commands for common workflows
├── skills/          # Reusable skill packages
└── reports/         # Generated reports and registries

openspec/            # Spec-driven development
```

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

Copy the `.claude/` and `openspec/` directories into your project. The infrastructure will adapt to your project's toolchain automatically.

## Documentation

See [CLAUDE.md](CLAUDE.md) for AI assistant instructions.
