---
description: Adapt the generic toolkit core to this project by populating .claude/project.md.
argument-hint: "[--refresh]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# Adapt Core to Project

Populate `.claude/project.md` — the single file that holds this project's
specifics — so the toolkit's **generic core** never needs hand-editing and can
be updated in place.

## How it works

`.claude/project.md` has two parts:

1. A managed `<!-- CORE:AUTODETECT -->` block — toolchain facts, regenerated
   deterministically. **Never edit it by hand.**
2. Free-form **Project-specific notes** — architecture, conventions, domain.
   Yours to own; preserved across reruns and core updates.

This command refreshes (1) via `adapt.py`, then fills in (2) from what it learns
about the repo. Safe to rerun any time — it updates the notes in place rather
than duplicating them.

## Steps

1. **Run the deterministic pass** (seeds `project.md`, refreshes the toolchain block):

   ```bash
   uv run --script .claude/skills/agent-coordination/scripts/adapt.py
   ```

2. **Read the project** to learn its specifics. Look at, as available:
   - `README*`, `CONTRIBUTING*`, `docs/`
   - Root config (`pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, Makefile, CI configs)
   - Top-level source layout and entry points
   - Existing `CLAUDE.md` / `AGENTS.md`

3. **Update the free-form sections of `.claude/project.md`** — and ONLY the
   parts below the `CORE:AUTODETECT:END` marker. Never touch the managed block.
   Fill in concisely:
   - **Architecture** — structure, key modules, entry points, data flow
   - **Conventions** — naming, branching, commit/PR style, definition of done
   - **Domain / glossary** — terms an agent must know
   - **Toolchain overrides** — only if an auto-detected command is wrong

4. **If commands were wrong**, record the correct ones under *Toolchain
   overrides* (these take precedence) rather than editing the managed block.

5. **Point CLAUDE.md at the profile** (one time). Ensure the project's
   `CLAUDE.md` tells agents to read project specifics from `@.claude/project.md`.
   Add a short line if missing; do not duplicate.

## Rules

- Keep `project.md` the **only** place project specifics live. Do not edit core
  files (`agents/`, `commands/`, `skills/`, scripts) to encode project details —
  those get overwritten on update.
- Be concise and factual; this is a reference agents read, not prose.
- `--refresh`: re-derive notes from the current repo state, updating stale
  entries while preserving still-accurate ones.

## Output

A populated, current `.claude/project.md`. Report a short summary of what you set
or changed.
