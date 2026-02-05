## ADDED Requirements

### Requirement: Client configuration documentation structure
The system SHALL provide MCP client configuration documentation in `docs/clients/` directory with one Markdown file per client using kebab-case naming convention.

#### Scenario: Documentation file exists for each supported client
- **WHEN** a user looks for configuration for any of the 20 supported MCP clients
- **THEN** a corresponding `docs/clients/<client-name>.md` file SHALL exist

#### Scenario: Documentation uses consistent naming
- **WHEN** creating documentation files
- **THEN** filenames SHALL use kebab-case (e.g., `claude-code.md`, `vs-code-copilot.md`)

### Requirement: Configuration file location section
Each client documentation SHALL include a "Config File Location" section specifying the configuration file path for Windows, macOS, and Linux where applicable.

#### Scenario: Windows path provided
- **WHEN** the client supports Windows
- **THEN** the documentation SHALL include the Windows configuration file path

#### Scenario: macOS path provided
- **WHEN** the client supports macOS
- **THEN** the documentation SHALL include the macOS configuration file path

#### Scenario: Linux path provided
- **WHEN** the client supports Linux
- **THEN** the documentation SHALL include the Linux configuration file path

### Requirement: Configuration example section
Each client documentation SHALL include a "Configuration" section with a complete, copy-paste ready JSON configuration block for Blender MCP.

#### Scenario: JSON configuration is complete
- **WHEN** a user copies the configuration example
- **THEN** it SHALL contain all required fields: server name, command, args, and env variables

#### Scenario: Configuration uses correct module path
- **WHEN** the configuration specifies the command
- **THEN** it SHALL use `python -m blender_mcp.mcp_protocol` as the entry point

### Requirement: Verification section
Each client documentation SHALL include a "Verification" section with steps to confirm MCP registration is successful.

#### Scenario: Verification steps are actionable
- **WHEN** a user follows the verification steps
- **THEN** the steps SHALL describe how to confirm the Blender MCP server appears in the client's server list

### Requirement: Troubleshooting section
Each client documentation SHALL include a "Troubleshooting" section with common issues and solutions.

#### Scenario: Common connection issues covered
- **WHEN** a user encounters connection problems
- **THEN** the troubleshooting section SHALL address: Python not found, PYTHONPATH issues, socket connection failures

### Requirement: README.md client configuration index
The README.md SHALL contain a "MCP Client Configuration" section with a table linking to all supported client documentation files.

#### Scenario: Index table format
- **WHEN** viewing the README.md client configuration section
- **THEN** it SHALL display a table with columns: Client Name, Link to Documentation

#### Scenario: All 20 clients listed
- **WHEN** counting entries in the client configuration table
- **THEN** all 20 supported clients SHALL be listed: Amp, Antigravity, Claude Code, Cline, Codex, Copilot CLI, Copilot / VS Code, Cursor, Factory CLI, Gemini CLI, Gemini Code Assist, JetBrains AI Assistant & Junie, Kiro, OpenCode, Qoder, Qoder CLI, Visual Studio, Warp, Windsurf

