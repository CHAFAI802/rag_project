@echo off
REM 🔍 RAG Logistics - Quick Verification Script (Windows)
REM Check if everything is ready before running the demo

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║           🔍 RAG System - Health Check                         ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check venv
echo [1/5] Checking Python virtual environment...
if exist ".venv\Scripts\activate.bat" (
    echo ✅ Virtual environment found
) else (
    echo ❌ Virtual environment not found - run: python -m venv .venv
    goto :error
)

REM Check frontend file
echo.
echo [2/5] Checking frontend application...
if exist "frontend_rag_demo.html" (
    echo ✅ frontend_rag_demo.html found
) else (
    echo ❌ frontend_rag_demo.html not found
    goto :error
)

REM Check app directory
echo.
echo [3/5] Checking backend application...
if exist "app\main.py" (
    echo ✅ Backend application found
) else (
    echo ❌ Backend application not found
    goto :error
)

REM Check FAISS index
echo.
echo [4/5] Checking FAISS vector index...
if exist "data\faiss\index.faiss" (
    echo ✅ FAISS index found
) else if exist "data\faiss_index\index.faiss" (
    echo ✅ FAISS index found (alternate location)
) else (
    echo ⚠️  FAISS index not found - may need to rebuild
    echo    Run: python setup_rag.py
)

REM Check test documents
echo.
echo [5/5] Checking test documents...
if exist "data\raw_docs" (
    for /f %%A in ('dir /b data\raw_docs\*.txt 2^>nul ^| find /c /v ""') do (
        if %%A GTR 0 (
            echo ✅ Test documents found: %%A documents
        ) else (
            echo ⚠️  No test documents found
        )
    )
) else (
    echo ⚠️  Test documents directory not found
)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║              ✅ All Checks Passed!                            ║
echo ║                                                                ║
echo ║  You can now run: start_rag_demo.bat                           ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
pause
goto :end

:error
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                                                                ║
echo ║              ❌ Setup Issue Detected                           ║
echo ║                                                                ║
echo ║  Please fix the above issues and try again                    ║
echo ║                                                                ║
echo ║  For help, see: FRONTEND_QUICKSTART.md                        ║
echo ║                                                                ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
pause
exit /b 1

:end
