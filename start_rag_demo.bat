@echo off
REM 🚚 RAG Logistics Frontend - Startup Script (Windows)
REM This script starts both the API and Frontend servers

setlocal enabledelayedexpansion

REM Get the project directory
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║          🚚 RAG Logistics - Frontend Demo Startup              ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if venv exists
if not exist ".venv" (
    echo ❌ ERROR: Virtual environment not found at .venv
    echo.
    echo Please create it first:
    echo   python -m venv .venv
    echo.
    pause
    exit /b 1
)

REM Check if frontend file exists
if not exist "frontend_rag_demo.html" (
    echo ❌ ERROR: frontend_rag_demo.html not found
    echo.
    echo Please ensure you're in the rag_project directory
    echo.
    pause
    exit /b 1
)

echo ✅ Starting RAG Logistics Demo...
echo.
echo Starting API Server (Port 8000)...
echo Starting Frontend Server (Port 8001)...
echo.
timeout /t 2 /nobreak

REM Start API in new terminal window
start "RAG API Server" cmd /k "cd /d "%cd%" && call .venv\Scripts\activate.bat && python -m uvicorn app.main:app --port 8000 --reload"

REM Wait a moment for API to start
timeout /t 3 /nobreak

REM Start Frontend in new terminal window
start "RAG Frontend Server" cmd /k "cd /d "%cd%" && call .venv\Scripts\activate.bat && python -m http.server 8001 --directory ."

REM Wait a moment for both to start
timeout /t 2 /nobreak

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║              ✅ Servers Starting...                            ║
echo ║                                                                ║
echo ║  API Server:      http://localhost:8000                        ║
echo ║  Frontend:        http://localhost:8001/frontend_rag_demo.html ║
echo ║  Swagger UI:      http://localhost:8000/docs                   ║
echo ║                                                                ║
echo ║  Opening browser in 3 seconds...                               ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Wait before opening browser
timeout /t 3 /nobreak

REM Try to open browser (works on Windows)
start http://localhost:8001/frontend_rag_demo.html

echo.
echo 📝 Two terminal windows have been opened:
echo    - Terminal 1: API Server (Ctrl+C to stop)
echo    - Terminal 2: Frontend Server (Ctrl+C to stop)
echo.
echo 🎯 Browser should open automatically to the frontend
echo.
echo 💡 Tips:
echo    - API Docs:  http://localhost:8000/docs
echo    - Health:    curl http://localhost:8000/health
echo    - Stop:      Close the terminal windows or press Ctrl+C
echo.
pause
