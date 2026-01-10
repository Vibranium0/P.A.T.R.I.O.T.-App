#!/bin/bash
echo "=== Checking if migration ran ===" 
echo ""
echo "Looking for migration output in start_all_fixed.sh logs..."
echo ""
/workspaces/P.A.T.R.I.O.T.-App/sentinel_login/backend/venv/bin/python3 /workspaces/P.A.T.R.I.O.T.-App/run_migrations.py
