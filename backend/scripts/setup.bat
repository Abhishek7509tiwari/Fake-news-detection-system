@echo off
cd /d "%~dp0.."
echo Cleaning up...
if exist venv rmdir /s /q venv

echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create venv. Trying global install as fallback...
    pip install -r requirements.txt
    goto :success
)

echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
:success
echo.
echo Setup complete.
pause
