#!/bin/bash
# Clean all node_modules, lock files, Python venvs, and Vite caches for a full reset (no restart)
# Usage: ./clean_all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Stopping all dev servers and backend processes (if running)..."
pkill -f 'python app.py' 2>/dev/null || true
pkill -f 'npm run dev' 2>/dev/null || true

echo "Removing node_modules and lock files for frontends..."
rm -rf patriot/frontend/node_modules patriot/frontend/package-lock.json
rm -rf sentinel_login/frontend/node_modules sentinel_login/frontend/package-lock.json

echo "Removing node_modules and lock files in shared (if present)..."
rm -rf shared/node_modules shared/package-lock.json

echo "Removing Python virtual environments..."
rm -rf patriot/backend/venv
rm -rf sentinel_login/backend/venv

echo "Clearing Vite caches..."
rm -rf patriot/frontend/node_modules/.vite
rm -rf sentinel_login/frontend/node_modules/.vite

echo "✅ Clean complete. You can now run bash start_all.sh for a fresh install."
