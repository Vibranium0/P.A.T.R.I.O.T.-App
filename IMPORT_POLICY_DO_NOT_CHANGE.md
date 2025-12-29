# DO NOT CHANGE: Monorepo Python Import/Package Policy

This repository is standardized for absolute imports and package structure. All contributors must follow these rules:

- Use only absolute imports from the monorepo root (see PYTHON_IMPORTS.md).
- Never use relative imports (e.g., from .models import X).
- All package directories must have an __init__.py file.
- Shared code must be imported as from shared....
- If you are unsure, consult PYTHON_IMPORTS.md or ask the team.

This file is a permanent reminder. Do not delete.
