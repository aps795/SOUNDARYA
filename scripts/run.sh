#!/usr/bin/env bash
# SOUNDARYA — Application Launcher Script

# Activate virtual environment if available
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run application (passes any CLI arguments like --cli or --debug)
python3 main.py "$@"
