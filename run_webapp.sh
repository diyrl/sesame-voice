#!/bin/bash

# Run CSM Speech Generator

# Stop any existing server
echo "Stopping any existing server processes..."
pkill -f "python app.py" 2>/dev/null || true

# Set environment variable to avoid Matplotlib error on Mac
export MPLBACKEND=Agg

# Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install Flask using uv if not installed
echo "Checking for Flask..."
if ! python -c "import flask" &> /dev/null; then
    echo "Installing Flask in the virtual environment using uv..."
    uv pip install flask
fi

# Make the static directory if it doesn't exist
mkdir -p static/audio outputs

# Get local IP address for easier access from other devices
if command -v ipconfig &> /dev/null; then
    # macOS
    LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "localhost")
elif command -v hostname &> /dev/null; then
    # Linux/Unix
    LOCAL_IP=$(hostname -I | awk '{print $1}' || echo "localhost")
else
    LOCAL_IP="localhost"
fi

# Run the Flask app
echo "======================================================="
echo "🔊 CSM Speech Generator is starting..."
echo "======================================================="
echo "✅ Access the web interface at:"
echo "   http://localhost:8080"
echo "   or"
echo "   http://$LOCAL_IP:8080"
echo "======================================================="
echo "Press Ctrl+C to stop the server when finished"
echo "======================================================="

# Start the Flask app
python app.py