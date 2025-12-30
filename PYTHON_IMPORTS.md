# Monorepo Python Import & Package Structure

## Overview
This monorepo uses absolute imports from the repository root for all Python code. This ensures reliable imports, easy refactoring, and compatibility with modern tooling and IDEs.

## Import Rules
- **Always use absolute imports** from the monorepo root, e.g.:
  - `from patriot.backend.models.bill import Bill`
  - `from shared.models.user import User`
  - `from sentinel_login.backend.models.user import User`
- **Never use relative imports** (e.g., `from .models import X` or `from ..utils import Y`).
- **Never use ambiguous or local imports** (e.g., `from models import X` or `import models`).
- **All package directories must have an `__init__.py` file** (even if empty or with a comment).
- **Shared code** (models, routes, utils) must be imported as `from shared...`.
- **Backend and frontend code** for each app should be kept in their respective subfolders.

## Example Directory Structure
```
P.A.T.R.I.O.T.-App/
  patriot/
    backend/
      models/
      routes/
      utils/
    frontend/
  sentinel_login/
    backend/
      models/
      routes/
      utils/
    frontend/
  shared/
    models/
    routes/
    utils/
```

## Example Imports
```python
from patriot.backend.models.bill import Bill
from shared.models.user import User
from sentinel_login.backend.models.user import User
```

## Adding New Code
- Place new modules in the appropriate package directory.
- Add an `__init__.py` if the directory is new.
- Use absolute imports as shown above.

## Troubleshooting
- If you get `ModuleNotFoundError`, check:
  - The import path is absolute from the repo root.
  - All parent directories have `__init__.py` files.
  - You are running Python from the repo root or with `PYTHONPATH` set to the repo root.

---

For questions, see this file or ask the team.
