@echo off
cd /d "%~dp0.."
if not exist venv (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b
)
call venv\Scripts\activate
streamlit run src\app_streamlit\app.py
