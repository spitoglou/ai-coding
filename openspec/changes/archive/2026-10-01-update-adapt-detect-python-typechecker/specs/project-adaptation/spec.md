## ADDED Requirements
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
