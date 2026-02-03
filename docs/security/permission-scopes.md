# Permission Scopes

## Overview
Each capability declares required permission scopes. Requests must provide all required scopes.

## Authorization Check
- Determine required scopes for capability
- Verify provided scopes are a superset
- Reject with missing_scope if not authorized
