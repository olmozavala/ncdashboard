#!/bin/bash

# Function to display help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --dev      Start the React app in development mode (yarn start)"
    echo "  -p PORT    Specify the port for serving the app"
    echo "  --help     Show this help message"
    exit 0
}

PORT=3000  # Default port
PORT_SPECIFIED=false

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --help)
            show_help
            ;;
        --dev)
            MODE="dev"
            shift
            ;;
        -p)
            PORT="$2"
            PORT_SPECIFIED=true
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if ! $PORT_SPECIFIED; then
    echo "Warning: No port specified. Using default port $PORT."
fi

# Check if Yarn is installed, install it if not
if ! command -v yarn &> /dev/null; then
    echo "Yarn is not installed. Installing..."
    npm install -g yarn
else
    echo "Yarn is already installed."
fi

# Install dependencies
echo "Installing dependencies..."
yarn install

# Check for --dev flag
if [[ "$MODE" == "dev" ]]; then
    echo "Starting the React app in development mode..."
    PORT=$PORT yarn start
else
    echo "Building and serving the React app..."
    yarn build
    yarn global add serve  # Install 'serve' if not installed
    serve -s dist -l $PORT
fi
