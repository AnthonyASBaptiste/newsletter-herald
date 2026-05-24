#!/bin/bash
# setup_cron.sh
# Run this script on your Debian 13 server to register the Sunday 8:00 AM delivery cron.

# Get the absolute path of the backend directory
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$BACKEND_DIR/venv/bin/python"
SCRIPT_PATH="$BACKEND_DIR/scripts/delivery_worker.py"
CRON_JOB="0 8 * * 7 cd $BACKEND_DIR && $PYTHON_BIN $SCRIPT_PATH >> $BACKEND_DIR/cron_delivery.log 2>&1"

echo "Configuring Linux Crontab for Weekly Delivery..."

# Check if Python exists in venv
if [ ! -f "$PYTHON_BIN" ]; then
    # Fallback to system python3 if venv doesn't exist yet
    PYTHON_BIN="python3"
    echo "Warning: Virtual environment python not found, falling back to system '$PYTHON_BIN'"
fi

# Check if the delivery script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Delivery worker script not found at $SCRIPT_PATH"
    exit 1
fi

# Add job to crontab if it doesn't already exist
(crontab -l 2>/dev/null | grep -F "$SCRIPT_PATH" >/dev/null)
if [ $? -eq 0 ]; then
    echo "Task is already registered in crontab."
else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Successfully registered Sunday 8:00 AM delivery task in crontab!"
    echo "Job details: $CRON_JOB"
fi
