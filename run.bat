@echo off
cd /d "%~dp0"
py -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
if not exist config.json copy config.example.json config.json
py app.py
