#!/bin/bash
# Sapphire Application Launcher
# This file automatically installs dependencies and launches the application

echo "Welcome to Sapphire!"
echo

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check for Python
if ! command_exists python3; then
    if ! command_exists python; then
        echo "Error: Python not found in the system."
        echo "Please install Python 3.8 or higher."
        echo
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Using Python: $PYTHON_CMD"

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo "Python version: $PYTHON_VERSION"

# Check for pip
if ! $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
    echo "Error: pip not found."
    echo "Please install pip for Python."
    echo
    exit 1
fi

# Check for requirements.txt file
if [[ ! -f "requirements/requirements.txt" ]]; then
    echo "Error: requirements/requirements.txt file not found."
    echo "Make sure all project files are in the correct locations."
    echo
    exit 1
fi

# Install dependencies
echo "Checking and installing dependencies..."
$PYTHON_CMD -m pip install -r requirements/requirements.txt --user --quiet

# Launch application
echo "Starting Sapphire..."
echo
$PYTHON_CMD source/sapphire.py

# Check exit code
if [[ $? -ne 0 ]]; then
    echo
    echo "An error occurred while starting the application."
    echo "Error code: $?"
    echo
    read -p "Press Enter to exit..."
fi
