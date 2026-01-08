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

# Setup and install Python dependencies
echo "Setting up Python virtual environments..."

# Patriot Backend
cd "$SCRIPT_DIR/patriot/backend"
echo "Creating Patriot backend venv..."
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt
deactivate

# Sentinel Backend
cd "$SCRIPT_DIR/sentinel_login/backend"
echo "Creating Sentinel backend venv..."
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt
deactivate

# Install Node dependencies
echo "Installing Node dependencies..."
cd "$SCRIPT_DIR/patriot/frontend"
npm install --silent

cd "$SCRIPT_DIR/sentinel_login/frontend"
npm install --silent

cd "$SCRIPT_DIR"

# Clear Vite caches for fresh start
echo "Clearing Vite caches..."
rm -rf "$SCRIPT_DIR/patriot/frontend/node_modules/.vite"
rm -rf "$SCRIPT_DIR/sentinel_login/frontend/node_modules/.vite"

# Create instance directories for databases
echo "Creating instance directories..."
mkdir -p "$SCRIPT_DIR/patriot/backend/instance"
mkdir -p "$SCRIPT_DIR/sentinel_login/backend/instance"

# Run database migrations (use sentinel venv if available)
echo "Running database migrations..."
if [ -f "$SCRIPT_DIR/sentinel_login/backend/venv/bin/python3" ]; then
  PYTHONPATH="$SCRIPT_DIR" "$SCRIPT_DIR/sentinel_login/backend/venv/bin/python3" "$SCRIPT_DIR/run_migrations.py" 2>&1 | tee "$SCRIPT_DIR/migration.log"
else
  PYTHONPATH="$SCRIPT_DIR" python3 "$SCRIPT_DIR/run_migrations.py" 2>&1 | tee "$SCRIPT_DIR/migration.log"
fi
echo "Migration output saved to migration.log"
echo ""

# Start Patriot Backend (run from workspace root with PYTHONPATH)
echo "Starting Patriot backend..."
cd "$SCRIPT_DIR"
PYTHONPATH="$SCRIPT_DIR" nohup "$SCRIPT_DIR/patriot/backend/venv/bin/python3" "$SCRIPT_DIR/patriot/backend/app.py" > "$SCRIPT_DIR/patriot_backend.log" 2>&1 &

# Start Patriot Frontend
cd "$SCRIPT_DIR/patriot/frontend"
nohup npm run dev > "$SCRIPT_DIR/patriot_frontend.log" 2>&1 &
cd "$SCRIPT_DIR"

# Start Sentinel Backend (run from workspace root with PYTHONPATH)
echo "Starting Sentinel backend..."
cd "$SCRIPT_DIR"
PYTHONPATH="$SCRIPT_DIR" nohup "$SCRIPT_DIR/sentinel_login/backend/venv/bin/python3" "$SCRIPT_DIR/sentinel_login/backend/app.py" > "$SCRIPT_DIR/sentinel_backend.log" 2>&1 &

# Start Sentinel Frontend
cd "$SCRIPT_DIR/sentinel_login/frontend"
nohup npm run dev > "$SCRIPT_DIR/sentinel_frontend.log" 2>&1 &
cd "$SCRIPT_DIR"

# Show status
sleep 3
echo "All Patriot and Sentinel apps started in background."
echo ""
echo "=== PORT CONFIGURATION ==="
echo "Patriot Backend:   http://localhost:5000"
echo "Patriot Frontend:  http://localhost:5173"
echo "Sentinel Backend:  http://localhost:5001"
echo "Sentinel Frontend: http://localhost:5175"
echo ""
echo "=== LOGS ==="
echo "Patriot Backend:   tail -f patriot_backend.log"
echo "Patriot Frontend:  tail -f patriot_frontend.log"
echo "Sentinel Backend:  tail -f sentinel_backend.log"
echo "Sentinel Frontend: tail -f sentinel_frontend.log"
echo ""
echo "To stop all: pkill -f 'python app.py' && pkill -f 'npm run dev'"
