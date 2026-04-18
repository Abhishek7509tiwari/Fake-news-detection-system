@echo off
title TruthSeeker AI - Full Stack
echo ============================================
echo    TruthSeeker AI - Starting Full Stack
echo ============================================
echo.

:: Start Flask backend in a new window
echo [1/2] Starting Flask Backend on http://127.0.0.1:5000 ...
start "TruthSeeker Backend" cmd /k "cd /d "%~dp0" && python backend\src\app_flask\app.py"

:: Brief pause to let backend boot
timeout /t 3 /nobreak >nul

:: Start React frontend in a new window
echo [2/2] Starting React Frontend on http://localhost:8080 ...
start "TruthSeeker Frontend" cmd /k "cd /d "%~dp0truthseeker ai frontend" && npm run dev"

:: Wait and open browser
timeout /t 5 /nobreak >nul
echo.
echo ============================================
echo    Both servers are running!
echo    Backend:  http://127.0.0.1:5000
echo    Frontend: http://localhost:8080
echo ============================================
echo.
echo Opening browser...
start http://localhost:8080
echo.
echo You can close this window. The servers run in their own windows.
pause
