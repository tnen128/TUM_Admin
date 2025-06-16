#!/bin/bash

# Get the absolute path of the project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Export the Python path
export PYTHONPATH="${PROJECT_DIR}:${PYTHONPATH}"

# Function to run the backend
run_backend() {
    echo "Starting backend server..."
    cd "$PROJECT_DIR"
    uvicorn app.api.main:app --reload
}

# Function to run the frontend
run_frontend() {
    echo "Starting frontend server..."
    cd "$PROJECT_DIR"
    streamlit run app/web/main.py
}

# Check if a specific component was requested
if [ "$1" == "backend" ]; then
    run_backend
elif [ "$1" == "frontend" ]; then
    run_frontend
else
    # Run both in separate terminals
    osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR' && ./run.sh backend\""
    osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR' && ./run.sh frontend\""
fi 