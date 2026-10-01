# Project Context

## Purpose
Reusable Claude Code infrastructure providing agent coordination, design systems, and spec-driven development with OpenSpec. Designed to be copied into any project.

## Infrastructure Components
- Agent Coordination - 15 specialized agents with registry tracking
- Design System - Consistent UI/UX patterns and color systems
- OpenSpec Integration - Spec-driven development workflow
- UV-based Scripts - Cross-platform Python utilities

## Project Conventions

### Code Style
Conventions are project-specific. Common patterns:
- Python: PEP 8, type hints
- JavaScript/TypeScript: ESLint/Prettier
- Rust: rustfmt, clippy
- Go: gofmt, golangci-lint

### Markdown & YAML
- Markdown: CommonMark specification
- YAML: 2-space indentation

### Architecture Patterns
- Agent-based task decomposition
- Registry-driven coordination
- Report-based knowledge persistence

### Testing Strategy
- Use project-appropriate test runner (auto-detected)
- Manual verification for agent workflows
- Report validation via verify.py script

### Git Workflow
- Main branch: `main`
- Feature branches: `feature/[description]`
- Conventional commits preferred (works with commitizen)

## Domain Context
This infrastructure provides AI-assisted software development using specialized agents for code review, security scanning, documentation, and more.

## Important Constraints
- Agents operate without shared memory - context must be injected
- Reports are the primary knowledge transfer mechanism
- OpenSpec changes require approval before implementation

## External Dependencies
- Anthropic Claude API (via Claude Code CLI)
- UV (for running infrastructure scripts)
- OpenSpec CLI for spec management (optional)
