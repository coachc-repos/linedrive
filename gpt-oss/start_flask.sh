#!/bin/bash

# Check if port 5001 is in use
if lsof -i :5001 > /dev/null; then
    echo "Port 5001 is in use. Attempting to free it..."
    kill -9 $(lsof -t -i :5001) 2>/dev/null
    sleep 1
fi

# Navigate to Flask app directory
cd /Users/christhi/Dev/Github/linedrive/gpt-oss-ui

# Start simple Flask server
echo "Starting Simple Flask server on http://localhost:5001..."
python flask_simple.py
