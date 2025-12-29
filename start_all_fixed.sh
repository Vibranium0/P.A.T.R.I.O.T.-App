#!/bin/bash
# Quick start script for Patriot and Sentinel apps (frontend & backend)
# Usage: ./start_all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Start Patriot Backend
echo "[DEBUG] CWD before Patriot Backend: $(pwd)"
ls -l
cd patriot/backend
echo "[DEBUG] CWD after cd patriot/backend: $(pwd)"
ls -l
if [ -f venv/bin/activate ]; then
  source venv/bin/activate
fi
PYTHONPATH=../.. nohup python app.py > ../../patriot_backend.log 2>&1 &
cd "$SCRIPT_DIR"

# Start Patriot Frontend
echo "[DEBUG] CWD before Patriot Frontend: $(pwd)"
ls -l
cd patriot/frontend
echo "[DEBUG] CWD after cd patriot/frontend: $(pwd)"
ls -l
nohup npm run dev > ../../patriot_frontend.log 2>&1 &
cd "$SCRIPT_DIR"

# Start Sentinel Backend
echo "[DEBUG] CWD before Sentinel Backend: $(pwd)"
ls -l
cd sentinel-login/backend
echo "[DEBUG] CWD after cd sentinel-login/backend: $(pwd)"
ls -l
if [ -f venv/bin/activate ]; then
  source venv/bin/activate
fi
PYTHONPATH=../.. nohup python app.py > ../../sentinel_backend.log 2>&1 &
cd "$SCRIPT_DIR"

# Start Sentinel Frontend
echo "[DEBUG] CWD before Sentinel Frontend: $(pwd)"
ls -l
cd sentinel-login/frontend
echo "[DEBUG] CWD after cd sentinel-login/frontend: $(pwd)"
ls -l
nohup npm run dev > ../../sentinel_frontend.log 2>&1 &
cd "$SCRIPT_DIR"

# Show status
sleep 2
echo "All Patriot and Sentinel apps started in background."
echo "Logs: patriot_backend.log, patriot_frontend.log, sentinel_backend.log, sentinel_frontend.log"
echo "To stop all: pkill -f 'python app.py' && pkill -f 'npm run dev'"
