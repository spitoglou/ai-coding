## v0.3.0 (2026-08-15)

### Migration required

If your `_registry.md` uses bullet entries (`- report-name | Status | Summary`),
rewrite them as table rows under the matching `### Category` heading:

```markdown
| [name.md](category/name.md) | YYYY-MM-DD | Status | One-line summary |
```

Run `validate_registry.py` to find every row needing attention — it now reports
bullet entries as errors instead of skipping them. Prefer `add_report.py` over
hand-editing from here on; it writes the row in the accepted shape.

### Fixed — `/archive` had never archived anything

- Fix `archive_reports.py` being unable to parse the registry format this repo
  ships. It matched a markdown table row carrying its own date column, but
  `_registry.md` and `_registry-template.md` both used a bullet list with the
  date supplied by an enclosing heading. Every line failed to match, so
  `/archive` was a no-op in every consumer since the feature was introduced —
  the archive directory stayed empty while entries aged indefinitely.

  **Resolution:** `add_report.py`, `validate_registry.py`, and
  `archive_reports.py` already agreed on the table row, so the templates were
  the stale side, not the parser. That row is now the one canonical format, and
  `SKILL.md` § *Registry Entry Format* is its single definition — `templates.md`
  and the registry legend point at it rather than restating it.

- Fix the two reasons this went unnoticed for so long:

  `validate_registry.py` — written specifically to "catch the drift that would
  make archive_reports.py silently no-op" — only inspected lines starting with
  `| [`. A registry written entirely in bullets validated clean with **0
  errors**. Bullet entries are now an error, with the expected form printed.

  `archive_reports.py` counted only lines it had parsed, so a total parse
  failure printed `Archived: 0, Remaining: 0` and exited 0 — indistinguishable
  from an empty registry. It now reports entry lines *seen* versus *parsed*, and
  exits 1 with a diagnosis when it understands none of a non-empty registry.

### Fixed

- Fix same-day archive runs truncating each other. The archive registry filename
  derives from the current date, so a second run reopened the same path with
  `'w'` and discarded the earlier batch — leaving those reports on disk under
  `archive/<category>/` with no row in any registry. Runs on the same day now
  merge. Latent until the parser was fixed, live the moment it was.
- Fix `bootstrap.py` replacing `YYYY-MM-DD` across the whole template, which
  rewrote the documented row format and archive filename into stale literal
  dates. Only the `**Last Updated:**` line is dated now.
- Fix `archive_reports.py` and `validate_registry.py` treating fenced code
  blocks as live registry rows, so a registry documenting its own format tripped
  its own tooling.
- Fix `arch/` and `architecture/`, `handoff/` and `handoffs/` all existing at
  once: `bootstrap.py` created one pair while the registry linked the other.
  v0.2.2 corrected `SKILL.md` but not `templates.md` or the registry itself.
  Settled on `architecture/` and `handoffs/` throughout.
- Fix `/agents:coverage`, `/postmortem`, `/slo`, and `/agents:ci` writing report
  names without their category prefix, contrary to the convention v0.2.2
  established.
- Remove dead code in `archive_reports.py` that treated every `###` heading as a
  category name, conflating the date headings and category headings that the
  registry uses on two different axes.

### Added

- `docs/` report category. The `docs` agent's output was listed as
  "(documentation files)" — no report, so no registry entry and no verify step.
  Documentation was the only work type leaving no trace in the registry, which
  made drift invisible to the protocol even though `/debt` tracks
  "Documentation — stale docs" as a debt type.
- `add_report.py --agent`, and `--scaffold` now emits the full `**Agent:** /
  **Date:** / **Status:**` header block from `templates.md`. That header was
  previously mandated by a template no command referenced, so almost nothing
  carried it; it is now produced by the tool rather than asked for in prose.

### Changed

- One status vocabulary — `Active`, `Completed`, `Superseded`, `Archived` —
  defined in `SKILL.md` and enforced by `validate_registry.py`. The report
  header, registry entry docs, and registry legend previously listed three
  different sets, disagreeing on `Draft` and `Archived` with no precedence rule.
  `Draft` is not valid; an in-progress report is `Active`. The RFC lifecycle
  statuses in `/rfc` are explicitly a separate axis, and say so.
- The registry no longer keeps an "Active (Last 3 Days)" section. It duplicated
  rows the by-category tables already hold, which `validate_registry.py` rejects
  as duplicates, and its 3-day window disagreed with the 7-day archive
  threshold, leaving 3-to-7-day-old entries governed by neither rule. Recency is
  the Date column.

### Tests

- Fix the `project` fixture copying the developer's local `.claude/reports/`.
  That state is gitignored working state, so whatever reports happened to be on
  the machine changed entry counts, archive batches, and parse totals under the
  tests. It now seeds fresh from the templates.
- Fix `test_archive_keeps_recent_report` hardcoding `2026-07-24` as a "recent"
  date. That stopped being true on 2026-07-31, and the test had been failing
  since. Dates are computed relative to today.
- Cover what shipped broken: the parse refusal, the same-day merge, the
  validator's blind spot, and the bootstrap date substitution. The previous
  suite only ever fed the archiver `add_report.py` output, which was already
  canonical — the shipped template format was never exercised, which is exactly
  how the bug reached release.

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
