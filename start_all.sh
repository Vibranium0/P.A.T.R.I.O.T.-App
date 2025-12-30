#!/bin/bash
# Quick start script for Patriot and Sentinel apps (frontend & backend)
# Usage: ./start_all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Start Patriot Backend
cd patriot/backend
if [ -f venv/bin/activate ]; then
  source venv/bin/activate
fi
PYTHONPATH=../.. nohup python app.py > ../../patriot_backend.log 2>&1 &
cd ../../..

# Start Patriot Frontend
cd patriot/frontend
nohup npm run dev > ../../patriot_frontend.log 2>&1 &
cd ../../..

# Start Sentinel Backend
cd sentinel_login/backend
if [ -f venv/bin/activate ]; then
  source venv/bin/activate
fi
PYTHONPATH=../.. nohup python app.py > ../../sentinel_backend.log 2>&1 &
cd ../../..

# Start Sentinel Frontend
cd sentinel_login/frontend
nohup npm run dev > ../../sentinel_frontend.log 2>&1 &
cd ../../..

# Show status
sleep 2
echo "All Patriot and Sentinel apps started in background."
echo "Logs: patriot_backend.log, patriot_frontend.log, sentinel_backend.log, sentinel_frontend.log"
echo "To stop all: pkill -f 'python app.py' && pkill -f 'npm run dev'"
