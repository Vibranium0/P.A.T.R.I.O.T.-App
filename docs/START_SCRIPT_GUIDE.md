# Step-by-Step Guide: Starting All Patriot & Sentinel Services

This guide explains how to use the universal start script to launch all backend and frontend services for both the Patriot and Sentinel apps.

## Prerequisites
- Ensure you have Python 3 and Node.js installed.
- All dependencies for each backend (in their `venv`) and frontend (`npm install`) should be installed.
- The script file is named `start_all_fixed.sh` and is located in the root of your monorepo (`P.A.T.R.I.O.T.-App`).

## Steps

1. **Open a Terminal**
   - You can use any terminal (VS Code, Terminal.app, iTerm, etc.).

2. **Navigate to the Monorepo Root**
   - Example:
     ```sh
     cd /Users/christian/Documents/Projects/P.A.T.R.I.O.T./P.A.T.R.I.O.T.-App
     ```

3. **Make the Script Executable (First Time Only)**
   - Run this command if you haven't already:
     ```sh
     chmod +x start_all_fixed.sh
     ```

4. **Run the Script**
   - Start all services with:
     ```sh
     ./start_all_fixed.sh
     ```
   - The script will:
     - Start the Patriot backend (Flask, Python)
     - Start the Patriot frontend (React, Vite)
     - Start the Sentinel backend (Flask, Python)
     - Start the Sentinel frontend (React, Vite)

5. **Check Logs**
   - Log files are created in the monorepo root:
     - `patriot_backend.log`
     - `patriot_frontend.log`
     - `sentinel_backend.log`
     - `sentinel_frontend.log`
   - Use `tail -f <logfile>` to monitor output, e.g.:
     ```sh
     tail -f patriot_backend.log
     ```

6. **Stopping All Services**
   - To stop all running servers, run:
     ```sh
     pkill -f 'python app.py' || true
     pkill -f 'python3 app.py' || true
     pkill -f 'npm run dev' || true
     ```

## Notes
- You can run the script from any directory; it will always start services from the correct locations.
- If you make code changes, stop all services and rerun the script to restart them.
- If you encounter errors, check the log files for details.

---
For troubleshooting or further automation, contact your dev lead or see the project documentation.
