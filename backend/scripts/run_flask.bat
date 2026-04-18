@echo off
cd /d "%~dp0.."
if not exist venv (
    echo Virtual environment not found. Please run scripts\setup.bat first.
    pause
    exit /b
)
call venv\Scripts\activate
echo Starting TruthSeeker Flask App...
venv\Scripts\python.exe src/app_flask/app.py
pause
