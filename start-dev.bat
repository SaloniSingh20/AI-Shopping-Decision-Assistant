@echo off
REM Shop AI - Development Server Startup Script for Windows
REM This script starts both backend (FastAPI) and frontend (Next.js)

echo.
echo ========================================
echo   Shop AI - Starting Development Servers
echo ========================================
echo.

REM Start Backend (FastAPI on port 8000)
echo [Backend] Starting FastAPI server on port 8000...
start "Shop AI Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend (Next.js on port 3000)
echo [Frontend] Starting Next.js server on port 3000...
start "Shop AI Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo   Servers Started Successfully!
echo ========================================
echo.
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo Press any key to exit this window...
echo (The servers will continue running in separate windows)
pause >nul
