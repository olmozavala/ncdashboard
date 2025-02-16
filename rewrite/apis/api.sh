#!/bin/bash

# Set the virtual environment directory name
VENV_DIR="venv"
PORT=8000  # Default port

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        --dev)
            MODE="dev"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install it first."
    exit 1
fi

# Create virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists. Activating..."
else
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

RED='\033[0;31m'
GREY='\e[38;5;240m'    
Color_Off='\033[0m'       

run_command() {
    local cmd="$1"
    echo -e "${GREY}"
    shift
    "$cmd" "$@" | tail -n 5 | awk '{print "-> " $0}'
    echo -e "${Color_Off}"
}

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    
    run_command pip install --upgrade pip 
    run_command pip install -r requirements.txt 
    
else
    echo -e "${RED}requirements.txt not found in '/apis'.${Color_Off}"
fi

if [[ "$MODE" == "dev" ]]; then
    fastapi dev --port $PORT
else
    fastapi run --port $PORT
fi
