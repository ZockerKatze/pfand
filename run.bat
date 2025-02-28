@echo off
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3 to run this application.
    pause
    exit /b 1
)

python run.py
pause 