#!/bin/bash

# Face Attendance System - Run Script
# Usage: ./run.sh [backend|frontend|both]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Face Attendance System Launcher${NC}"
echo -e "${GREEN}========================================${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.10+${NC}"
    exit 1
fi

# Function to run backend
run_backend() {
    echo -e "${YELLOW}Starting Backend Server...${NC}"
    cd "$SCRIPT_DIR/backend"

    # Check if venv exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate venv
    source venv/bin/activate

    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt -q

    # Run server
    echo -e "${GREEN}Backend running at http://localhost:8000${NC}"
    echo -e "${GREEN}API Docs at http://localhost:8000/docs${NC}"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Function to run frontend
run_frontend() {
    echo -e "${YELLOW}Starting Frontend Server...${NC}"
    cd "$SCRIPT_DIR/frontend"

    # Check if venv exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate venv
    source venv/bin/activate

    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt -q

    # Run Streamlit
    echo -e "${GREEN}Frontend running at http://localhost:8501${NC}"
    streamlit run app.py
}

# Parse arguments
case "${1:-both}" in
    backend)
        run_backend
        ;;
    frontend)
        run_frontend
        ;;
    both)
        echo -e "${YELLOW}Starting both servers...${NC}"
        echo "Run in separate terminals:"
        echo "  ./run.sh backend"
        echo "  ./run.sh frontend"
        echo ""
        echo "Or run backend now (start frontend in another terminal):"
        run_backend
        ;;
    *)
        echo "Usage: $0 [backend|frontend|both]"
        exit 1
        ;;
esac
