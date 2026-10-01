# project-adaptation Specification

## Purpose
TBD - created by archiving change update-adapt-write-only-on-change. Update Purpose after archive.
## Requirements
### Requirement: AUTODETECT block written only on a real change
`adapt.py` SHALL rewrite the `CORE:AUTODETECT` block in `.claude/project.md` only when a
detected toolchain value differs from what the block already records. The recorded
date SHALL change only together with a detected value, never on its own.

#### Scenario: Unchanged toolchain on a later day
- **WHEN** `adapt.py` runs on a project whose block already records the detected values under an earlier date
- **THEN** `.claude/project.md` is not written and keeps its earlier date

#### Scenario: Changed toolchain
- **WHEN** a detected value differs from the block
- **THEN** the block is rewritten with the new values and today's date

#### Scenario: No generated block yet
- **WHEN** the markers hold no generated block, as in a freshly seeded `project.md`
- **THEN** the block is written with today's date

#### Scenario: Consecutive runs
- **WHEN** `adapt.py` runs twice on an unchanged project
- **THEN** `.claude/project.md` is byte-identical after the second run

### Requirement: Newline style preserved
When `adapt.py` writes `.claude/project.md` it SHALL keep the file's existing newline
style rather than converting it to the platform default, and seeding the file from
`project-template.md` SHALL copy the template's bytes unchanged.

#### Scenario: LF file on Windows
- **WHEN** `project.md` uses LF line endings and the block must be rewritten
- **THEN** the written file contains no CRLF

#### Scenario: CRLF file
- **WHEN** `project.md` uses CRLF line endings and the block must be rewritten
- **THEN** the rewritten block uses CRLF too

### Requirement: Python type checker detected
For a project with a `pyproject.toml`, `adapt.py` SHALL detect the type checker from that
file instead of assuming one. It SHALL recognise basedpyright (`uv run basedpyright`),
pyright (`uv run pyright`) and mypy (`uv run mypy .`) declared as a development dependency
(`[dependency-groups]`, `[tool.uv] dev-dependencies`, `[project.optional-dependencies]`,
Poetry dev groups) or configured in a `[tool.<checker>]` section. A declared dependency
SHALL outrank a configuration section, and among several the precedence SHALL be
basedpyright, pyright, mypy. When none is found the row SHALL read
"(configure in Toolchain overrides)".

#### Scenario: basedpyright project
- **WHEN** `[dependency-groups]` lists `basedpyright`
- **THEN** the Type check row is `uv run basedpyright`

#### Scenario: mypy project
- **WHEN** the dev dependencies list `mypy`
- **THEN** the Type check row is `uv run mypy .`

#### Scenario: No checker declared
- **WHEN** no recognised checker appears in dependencies or `[tool.*]` sections
- **THEN** the Type check row is "(configure in Toolchain overrides)"

#### Scenario: More than one checker
- **WHEN** both basedpyright and mypy are declared as dependencies
- **THEN** the Type check row is `uv run basedpyright`

#### Scenario: Dependency outranks configuration section
- **WHEN** basedpyright is a dependency and a `[tool.pyright]` section is present
- **THEN** the Type check row is `uv run basedpyright`

