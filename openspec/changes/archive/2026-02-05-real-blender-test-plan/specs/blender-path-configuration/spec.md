# Blender Path Configuration

## Purpose

支持配置和发现本地 Blender 可执行文件路径，按版本组织，供测试基础设施使用。

## ADDED Requirements

### Requirement: JSON configuration file for Blender paths

The project SHALL support a JSON configuration file for defining multiple Blender executable paths with version metadata.

#### Scenario: Load configuration from default path

- **WHEN** `load_blender_configs()` is called without arguments
- **THEN** it SHALL load from `tests/blender-paths.json` if the file exists

#### Scenario: Configuration file structure

- **WHEN** a configuration file is created
- **THEN** it SHALL contain an array of objects with `version`, `path`, and optional `tags` fields

#### Scenario: Configuration file is gitignored

- **WHEN** the repository is cloned
- **THEN** `tests/blender-paths.json` SHALL NOT be tracked in version control

### Requirement: Environment variable override

The configuration loader SHALL support environment variable override for CI flexibility.

#### Scenario: Override config path via environment

- **WHEN** `BLENDER_TEST_PATHS` environment variable is set
- **THEN** the loader SHALL use the specified path instead of the default

#### Scenario: Single Blender path via environment

- **WHEN** `BLENDER_EXECUTABLE` environment variable is set
- **THEN** the loader SHALL include this path as an additional Blender configuration

### Requirement: Path validation on load

The configuration loader SHALL validate that configured Blender paths exist and are executable.

#### Scenario: Validate path exists

- **WHEN** configuration is loaded
- **THEN** each configured path SHALL be checked for existence

#### Scenario: Report invalid paths

- **WHEN** a configured path does not exist
- **THEN** the loader SHALL log a warning and exclude that entry from results

#### Scenario: Detect Blender version from executable

- **WHEN** a valid Blender path is found
- **THEN** the loader SHALL optionally verify the version by running `blender --version`

### Requirement: Example configuration template

The project SHALL provide an example configuration file as a template for users.

#### Scenario: Template file in repository

- **WHEN** a user wants to configure Blender paths
- **THEN** they SHALL find `tests/blender-paths.example.json` with documented structure

#### Scenario: Template contains placeholder paths

- **WHEN** the example file is read
- **THEN** it SHALL contain example paths for Windows, Linux, and macOS with comments

