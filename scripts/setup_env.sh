#!/usr/bin/env bash
# SOUNDARYA — Environment Setup Script
set -e

echo "=========================================================="
echo "  SOUNDARYA — Personal AI Operating Assistant Setup"
echo "=========================================================="

# Create virtual environment if not present
if [ ! -d "venv" ]; then
    echo "[-] Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "[-] Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "[-] Installing requirements..."
pip install -r requirements.txt

# Create .env from template if missing
if [ ! -f ".env" ]; then
    echo "[-] Creating .env from .env.example..."
    cp .env.example .env
fi

# Initialize database schema
echo "[-] Initializing database..."
python -c "from app.database.db_engine import db_engine; print('Database ready at:', db_engine.db_path)"

echo "=========================================================="
echo "  Setup Completed Successfully!"
echo "  Run ./scripts/run.sh or python main.py to launch."
echo "=========================================================="
