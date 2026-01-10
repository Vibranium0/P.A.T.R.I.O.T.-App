## Node.js Frontend Environment Setup

### Patriot Frontend
1. Navigate to the frontend folder:
  ```sh
  cd patriot/frontend
  ```
2. Install dependencies:
  ```sh
  npm install
  ```

### Sentinel Frontend
1. Navigate to the frontend folder:
  ```sh
  cd sentinel_login/frontend
  ```
2. Install dependencies:
  ```sh
  npm install
  ```

> **Tip:** Use the same Node.js version for both frontends. Consider using an `.nvmrc` file to specify the Node version (e.g., `18.x`).
# P.A.T.R.I.O.T. Monorepo

## Overview
This monorepo houses multiple applications and a shared directory for common assets, components, and styles. The structure is designed for scalability, maintainability, and easy cross-app sharing.

### Apps
- **patriot**: The main budgeting and financial management app.
- **sentinel_login**: A companion app for registration, login, and user management. It provides:
  - A registration page with the Sentinel Systems color scheme.
  - A login page for each app, using that app's color scheme and background image.

### Shared Directory
- **shared/**: Not an app. Contains elements (assets, styles, components, utilities) used by multiple apps.

## Frontend Architecture
- **SPA Routing**: `sentinel_login` uses single-page app routing (e.g., React Router) to switch between registration and multiple login pages. Each login page uses the theme and background of its respective app.
- **Theme Management**: Themes are managed using CSS variables. Each app has its own theme CSS file (e.g., `patriot-theme.css`, `sentinel-theme.css`). Shared effects, fonts, and animations are imported from common CSS files in `shared/styles/`.
- **Background Images**: Each login/registration page uses a specific background image, set via CSS or as a prop to a shared layout component.
- **Shared Components**: UI components, hooks, and utilities that are used across apps are placed in `shared/ui/`.

## Folder Structure (Planned)
```
/P.A.T.R.I.O.T.-App
  /patriot
    /frontend/src/assets
    /frontend/src/styles
    /frontend/src/shared
    ...
  /sentinel_login
    /frontend/src/assets
    /frontend/src/styles
    /frontend/src/shared
    ...
  /shared
    /assets/patriot
    /assets/sentinel
    /assets/common
    /styles/effects.css
    /styles/fonts.css
    /styles/patriot-theme.css
    /styles/sentinel-theme.css
    /styles/common.css
    /ui/components
    /ui/hooks
    /ui/utils
```

## Key Principles

## Python Backend Environment Setup

### Patriot Backend
1. Navigate to the backend folder:
  ```sh
  cd patriot/backend
  ```
2. Create and activate a virtual environment (if not already present):
  ```sh
  python3 -m venv venv
  source venv/bin/activate
  ```
3. Install dependencies:
  ```sh
  pip install -r requirements.txt
  ```

### Sentinel Backend
1. Navigate to the backend folder:
  ```sh
  cd sentinel_login/backend
  ```
2. Create and activate a virtual environment (if not already present):
  ```sh
  python3 -m venv venv
  source venv/bin/activate
  ```
3. Install dependencies:
  ```sh
  pip install -r requirements.txt
  ```

> **Tip:** Always activate the correct virtual environment before running backend servers or scripts.


## 📚 Documentation

For complete setup, usage, and API details, see:

- [Quick Reference & Setup Guide](docs/QUICK_REFERENCE.md)
- [API Endpoints Documentation](docs/API_ENDPOINTS.md)

## Next Steps

This README will be updated as the project evolves and more implementation details are finalized.
