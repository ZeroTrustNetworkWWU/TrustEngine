#!/bin/bash

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    # Activate existing venv
    source venv/bin/activate
fi

# Start TrustEngine.py directly
venv/bin/python src/TrustEngine.py