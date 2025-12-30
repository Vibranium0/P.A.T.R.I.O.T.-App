#!/bin/bash
# Quick start script for Patriot and Sentinel apps (frontend & backend)
# Usage: ./start_all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Kill any existing processes on ports 5000, 5001, 5173, 5175
echo "Killing existing processes on ports 5000, 5001, 5173, 5175..."
pkill -9 -f 'python.*app.py' 2>/dev/null || true
pkill -9 -f 'npm run dev' 2>/dev/null || true
lsof -ti:5000,5001,5173,5174,5175 | xargs kill -9 2>/dev/null || true
sleep 2

# Start Patriot Backend
cd "$SCRIPT_DIR/patriot/backend"
if [ -f venv/bin/activate ]; then
  source venv/bin/activate
fi
PYTHONPATH="$SCRIPT_DIR" python3 app.py &
cd "$SCRIPT_DIR"

# Start Patriot Frontend
cd "$SCRIPT_DIR/patriot/frontend"
nohup npm run dev > "$SCRIPT_DIR/patriot_frontend.log" 2>&1 &
cd "$SCRIPT_DIR"

# Start Sentinel Backend
cd "$SCRIPT_DIR/sentinel_login/backend"
if [ -f venv/bin/activate ]; then
  source venv/bin/activate
fi
PYTHONPATH="$SCRIPT_DIR" python3 app.py &
cd "$SCRIPT_DIR"

# Start Sentinel Frontend
cd "$SCRIPT_DIR/sentinel_login/frontend"
nohup npm run dev > "$SCRIPT_DIR/sentinel_frontend.log" 2>&1 &
cd "$SCRIPT_DIR"

# Show status
sleep 2
echo "All Patriot and Sentinel apps started in background."
echo "Logs: patriot_backend.log, patriot_frontend.log, sentinel_backend.log, sentinel_frontend.log"
echo "To stop all: pkill -f 'python app.py' && pkill -f 'npm run dev'"
