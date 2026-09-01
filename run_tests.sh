#!/usr/bin/env bash
set -euo pipefail

# Start Flask app in background
python app.py &
APP_PID=$!

cleanup() {
    kill "$APP_PID" 2>/dev/null || true
}
trap cleanup EXIT

# Wait for app to be ready
sleep 5

# Run tests
pytest test_e2e.py -v
