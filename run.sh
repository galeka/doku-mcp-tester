#!/bin/bash
cd "$(dirname "$0")"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
if [ ! -f config.json ]; then
  cp config.example.json config.json
fi
python3 app.py
