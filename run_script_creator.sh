#!/bin/bash

# Direct LineDrive 4-Agent Script Creator
echo "🎬 Starting LineDrive 4-Agent Script Creator..."

# Activate virtual environment
source /Users/christhi/Dev/Github/.venv/bin/activate

# Change to the correct directory
cd /Users/christhi/Dev/Github/linedrive

# Run the script creator directly
python3 -c "
import asyncio
import sys
sys.path.append('/Users/christhi/Dev/Github/linedrive')
from console_launcher import run_script_to_demo_workflow

asyncio.run(run_script_to_demo_workflow())
"

echo "👋 Script creation completed!"
