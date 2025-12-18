#!/bin/bash

# Check if the required argument (dept_id) is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <dept_id> [limit]"
    echo "Example: $0 45 1000"
    exit 1
fi

# Assign the input arguments to meaningful variables
DEPT_ID="$1"
# Use $2 for the limit if provided, otherwise default to 500
LIMIT=${2:-500} 
PYTHON_SCRIPT="fetch_met_museum_data.py"

echo "Running script for Department ID: $DEPT_ID"
echo "Using Limit: $LIMIT"

# Execute the command
python "$PYTHON_SCRIPT" "$DEPT_ID" -l "$LIMIT"

echo "Script execution complete."