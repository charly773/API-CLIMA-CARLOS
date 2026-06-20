#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

# Activate the local virtual environment.
source .venv/bin/activate

# Install dependencies if needed.
pip install --no-cache-dir -r requirements.txt

# Run the application.
python app.py
