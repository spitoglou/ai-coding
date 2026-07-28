## v0.2.1 (2026-07-28)

- Fix Windows cp1252 crashes across the coordination scripts: all text-mode
  file I/O now specifies `encoding="utf-8"`, and script entry points force
  UTF-8 on stdout/stderr so piped output no longer raises UnicodeEncodeError.
  Projects whose reports, registry, or `project.md` contain non-ASCII text
  now work on Windows. No behavior change on Linux/macOS.
- Fix `validate_registry.py` reporting every registered report as an
  unregistered orphan on Windows, which made `--strict` always fail.

## v0.2.0 (2026-01-13)
