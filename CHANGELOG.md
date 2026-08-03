## v0.2.2 (2026-08-03)

### Fixed — definitions that silently failed to load

- Fix 10 of 15 agents failing to load. `architect`, `code-quality`,
  `data-engineer`, `devops`, `docs`, `ml-engineer`, `rfc`, `security-engineer`,
  `sre`, and `ux-designer` were absent from the agent registry, so invoking any
  of them failed with `Agent type '<name>' not found`. That broke
  `/agents:review`, `/agents:security`, `/review-full` (all four levels),
  `/rfc`, `/slo`, `/postmortem`, and `/debt`.

  **Root cause:** their `description:` value contained an unquoted `: `
  (e.g. `... Modes: scan (OWASP/CVE) ...`). Frontmatter is parsed as YAML, and
  YAML reads that second colon as another mapping key — a `ScannerError` that
  rejects the whole block. The definition is then dropped with no warning. The
  fix quotes the value; no wording changed.

  The same 10 files also carried a `mode:` key, which is the cause an earlier
  analysis identified. It is not: `mode: scan | threat-model` parses as a plain
  string. The key was removed anyway as redundant — modes are documented in each
  agent's `description` and body, and callers pass a mode in the prompt — but it
  was never what broke loading.

- Fix `/agents:review`, `/agents:security`, `/agents:ci`, `/agents:coverage`,
  and `/session:context` losing their frontmatter to the same YAML error, via
  `name: Agents: Review`. They appeared in the command list described as
  `**Purpose**` — their first body line — because the loader fell back to it.
  Dropped the unsupported `name`, `category`, and `tags` keys.
- Fix `argument-hint: [days]` in `/archive` and `/test` parsing as a YAML list
  rather than text, and add the missing frontmatter to `/release`.
- Fix `/review-full` declaring `allowed-tools: Read, Glob, Grep, Bash` — without
  `Task` it could not spawn the four agents it is built around, and without
  `Write` it could not save its own summary report.

### Added

- `validate_frontmatter.py` lints `.claude/agents/*.md` and
  `.claude/commands/**/*.md` with a real YAML parser, checking that each block
  parses, carries only supported keys, has its required keys, and yields text
  rather than a list. `bootstrap.py` runs it on install and `/agents:ci` runs it
  in CI, so this class of error fails loudly at setup instead of silently at
  dispatch.

### Changed — `/agents:review` and `/review-full` now interoperate

- Report naming is now `[category]-[topic]-[scope]-YYYY-MM-DD.md` everywhere,
  specified once in the `agent-coordination` skill. `/review-full` previously
  wrote scope-less names (`L1-peer-DATE.md`), so reviewing two paths on one day
  overwrote the first report and produced a duplicate registry row that
  `validate_registry.py` rejects.
- Each `/review-full` level now writes the same report its standalone
  equivalent writes — L1 ≡ `/agents:review`, L3 ≡ `/agents:security` — so a
  level already covered today is reused instead of re-run, and the summary can
  aggregate reports from either entry point.
- One severity vocabulary (BLOCKING / NON-BLOCKING / NIT) across all review
  reports, with a documented mapping to the tech-debt registry's Severity
  column. `/agents:review` previously specified none.
- Both commands now register reports with `add_report.py` instead of
  hand-editing `_registry.md`, which is the only way to get the row format
  `validate_registry.py` accepts.
- `/review-full` now writes deferred findings as `_tech-debt.md` **table rows**;
  it previously specified a bullet-list format the registry has no place for,
  under an `Impact:` label where the registry uses `Severity`.
- Corrected the report-category table in the `agent-coordination` skill: it
  documented `arch/` and `handoff/`, but `bootstrap.py` creates — and the
  registry template has headings for — `architecture/` and `handoffs/`.
- Corrected the coordination reference, which showed `mode` as a `Task()`
  parameter. It is not one — modes are conveyed in the prompt text.

## v0.2.1 (2026-07-28)

- Fix Windows cp1252 crashes across the coordination scripts: all text-mode
  file I/O now specifies `encoding="utf-8"`, and script entry points force
  UTF-8 on stdout/stderr so piped output no longer raises UnicodeEncodeError.
  Projects whose reports, registry, or `project.md` contain non-ASCII text
  now work on Windows. No behavior change on Linux/macOS.
- Fix `validate_registry.py` reporting every registered report as an
  unregistered orphan on Windows, which made `--strict` always fail.

## v0.2.0 (2026-01-13)
