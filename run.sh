#!/bin/bash

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="${PROJECT_DIR}:${PYTHONPATH}"

source "$PROJECT_DIR/venv/bin/activate"

run_backend() {
    echo "Starting backend server..."
    cd "$PROJECT_DIR"
    uvicorn app.api.main:app --reload
}

run_frontend() {
    echo "Starting frontend server..."
    cd "$PROJECT_DIR"
    streamlit run app/web/main.py
}

# Detect OS (macOS vs Linux/WSL)
OS="$(uname)"
IS_MAC=false
IS_WSL=false

if [[ "$OS" == "Darwin" ]]; then
    IS_MAC=true
elif grep -qi microsoft /proc/version; then
    IS_WSL=true
fi

# Run based on input
if [ "$1" == "backend" ]; then
    run_backend
elif [ "$1" == "frontend" ]; then
    run_frontend
else
    if [ "$IS_MAC" = true ]; then
        # Use macOS Terminal to run both scripts
        osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR' && ./run.sh backend\""
        osascript -e "tell application \"Terminal\" to do script \"cd '$PROJECT_DIR' && ./run.sh frontend\""
    else
        # Default (Linux/WSL): Run both in background in same terminal
        run_backend & 
        run_frontend & 
        wait
    fi
fi
