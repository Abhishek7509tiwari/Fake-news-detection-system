@echo off
cd /d "%~dp0.."
if not exist venv (
    echo Virtual environment not found. Please run scripts\setup.bat first.
    pause
    exit /b
)
call venv\Scripts\activate
echo Running Prediction CLI (Gemini API)...
python src/cli/main.py %*
pause
