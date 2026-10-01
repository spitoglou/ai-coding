## ADDED Requirements
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
