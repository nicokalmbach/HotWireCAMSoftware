@echo off
cd /d "%~dp0"
"%~dp0.venv\Scripts\python.exe" "%~dp0app.py" --open-browser
if errorlevel 1 pause
