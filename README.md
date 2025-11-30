# P.A.T.R.I.O.T. Monorepo

## Overview
This monorepo houses multiple applications and a shared directory for common assets, components, and styles. The structure is designed for scalability, maintainability, and easy cross-app sharing.

### Apps
- **patriot**: The main budgeting and financial management app.
- **sentinel-login**: A companion app for registration, login, and user management. It provides:
  - A registration page with the Sentinel Systems color scheme.
  - A login page for each app, using that app's color scheme and background image.

### Shared Directory
- **shared/**: Not an app. Contains elements (assets, styles, components, utilities) used by multiple apps.

## Frontend Architecture
- **SPA Routing**: `sentinel-login` uses single-page app routing (e.g., React Router) to switch between registration and multiple login pages. Each login page uses the theme and background of its respective app.
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
  /sentinel-login
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
- Each app has its own assets and styles, but can import from `shared` for cross-app consistency.
- Theme switching is handled via CSS variables and route-based imports.
- Shared effects, fonts, and animations are globally imported.
- Shared assets (like logos) may exist in both app-specific and shared locations for flexibility.

## Next Steps
- Implement SPA routing in `sentinel-login`.
- Set up theme CSS files and shared styles.
- Organize assets and components according to the planned structure.

---
This README will be updated as the project evolves and more implementation details are finalized.
