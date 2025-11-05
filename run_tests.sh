#!/bin/bash
set -e

# Start Flask app in background
python app.py &
APP_PID=$!

# Wait for app to be ready
sleep 5

# Run tests and capture exit code
pytest test_e2e.py -v
TEST_EXIT=$?

# Clean up: kill the Flask app
kill $APP_PID 2>/dev/null || true

# Exit with test exit code
exit $TEST_EXIT

