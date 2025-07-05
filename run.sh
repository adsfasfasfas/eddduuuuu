#!/bin/bash

# This script automates the entire launch process for EduGuideBot,
# ensuring all services start in the correct order and shut down cleanly.

set -ex # Exit immediately if a command exits with a non-zero status.


echo "--- Ensuring no previous instances are running ---"

# Function to kill processes by pattern
kill_process_by_pattern() {
    local pattern="$1"
    echo "Attempting to kill processes matching: '$pattern'"
    PIDS=$(pgrep -f "$pattern" || true)
    if [ -n "$PIDS" ]; then
        echo "Found PIDS: $PIDS. Killing..."
        kill $PIDS 2>/dev/null || true
        sleep 3 # Increased sleep time for processes to terminate
        if pgrep -f "$pattern" > /dev/null; then
            echo "❌ Process matching '$pattern' still running after kill attempt. PIDs: $(pgrep -f "$pattern")"
        else
            echo "✅ Process matching '$pattern' successfully terminated."
        fi
    else
        echo "No processes found matching: '$pattern'."
    fi
}

# Kill http.server processes by port
echo "Attempting to kill processes on port 8000 (http.server)"
HTTP_SERVER_PID=$(lsof -t -i :8000 || true)
if [ -n "$HTTP_SERVER_PID" ]; then
    echo "Found http.server PID: $HTTP_SERVER_PID. Killing..."
    kill $HTTP_SERVER_PID 2>/dev/null || true
    sleep 3
    if lsof -t -i :8000 > /dev/null; then
        echo "❌ http.server (PID $HTTP_SERVER_PID) still running after kill attempt."
    else
        echo "✅ http.server (PID $HTTP_SERVER_PID) successfully terminated."
    fi
else
    echo "No http.server found on port 8000."
fi

kill_process_by_pattern "./ngrok http 8000"
kill_process_by_pattern "python3 -m src.bot.app"

sleep 2 # Give all processes a moment to fully terminate

echo "--- 🚀 Launching EduGuideBot ---"

# Check for TELEGRAM_BOT_TOKEN
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ FATAL ERROR: TELEGRAM_BOT_TOKEN environment variable is not set."
    echo "Please set it in your .env file or as an environment variable."
    exit 1
fi

# Function to ensure background processes are killed on exit
cleanup() {
    echo "\n--- 🛑 Shutting down background services ---"
    # Kill http.server processes by port
    echo "Attempting to kill processes on port 8000 (http.server) during cleanup"
    HTTP_SERVER_PID=$(lsof -t -i :8000 || true)
    if [ -n "$HTTP_SERVER_PID" ]; then
        echo "Found http.server PID: $HTTP_SERVER_PID. Killing..."
        kill $HTTP_SERVER_PID 2>/dev/null || true
        sleep 1
    fi
    kill_process_by_pattern "./ngrok http 8000"
    kill_process_by_pattern "python3 -m src.bot.app"
    echo "✅ Cleanup complete. Goodbye!"
}

# Ensure previous instances are stopped before starting
echo "--- Ensuring no previous instances are running ---"
pkill -f "python3 -m http.server 8000" 2>/dev/null || true
pkill -f "./ngrok http 8000" 2>/dev/null || true
pkill -f "python3 -m src.bot.app" 2>/dev/null || true
sleep 1 # Give processes a moment to terminate


# Trap ensures the cleanup function is called on script exit (including Ctrl+C)
trap cleanup EXIT

# Clear the ngrok log file before starting
> ngrok.log

# Step 1: Activate the Python virtual environment.
echo "[1/4] Activating Python virtual environment..."
source venv/bin/activate
echo "DEBUG: Virtual environment activated."

# Install/update Python dependencies
echo "[1.5/4] Installing/updating Python dependencies..."
pip install -r requirements.txt
echo "DEBUG: Python dependencies installed."


# Step 2: Start the local web server in the background.
# The server hosts the web app files (HTML, CSS, JS).
echo "[2/4] Starting local web server for Web Apps..."
python3 -m http.server 8000 --directory . &
SERVER_PID=$!
echo "✅ Local web server started with PID $SERVER_PID. Checking if it's accessible..."
sleep 3 # Give the server a bit more time to start
if curl -s http://localhost:8000 > /dev/null; then
    echo "✅ Local web server is accessible on port 8000."
else
    echo "❌ Local web server is NOT accessible on port 8000. Check for port conflicts or firewall issues."
    exit 1
fi

# Step 3: Start ngrok and capture the public URL.
echo "[3/4] Starting ngrok tunnel..."
./ngrok http 8000 --log=ngrok.log &
NGROK_PID=$!
echo "✅ ngrok tunnel process started with PID $NGROK_PID."
echo "--> Waiting for ngrok to initialize (increased sleep to 10 seconds)..."
sleep 10 # Increased sleep time to allow ngrok to fully initialize

# Continuously check for the ngrok URL until it's available or we time out.
echo "--> Waiting for ngrok public URL..."
MAX_WAIT=20 # 20 seconds max
WAIT_COUNT=0
NGROK_URL=""

# Use grep to get the URL from the ngrok log file
while [ -z "$NGROK_URL" ] && [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    NGROK_URL=$(grep -o 'url=https://[^ ]*' ngrok.log | head -n 1 | sed 's/url=//')
    if [ -z "$NGROK_URL" ]; then
        echo "--> ngrok URL not available yet. Retrying... (${WAIT_COUNT}/${MAX_WAIT})"
        sleep 3 # Increased sleep for URL check
        ((WAIT_COUNT++))
    fi
done

if [ -z "$NGROK_URL" ]; then
    echo "❌ FATAL ERROR: Could not get ngrok URL after ${MAX_WAIT} seconds. Displaying ngrok log for debugging:"
    cat ngrok.log # Display ngrok log on failure
    exit 1
fi

export NGROK_URL
echo "✅ Public URL obtained: $NGROK_URL"

# Step 4: Run the main bot application.
echo "[4/4] Starting the Telegram bot... (Press Ctrl+C to stop)"
python3 -m src.bot.app