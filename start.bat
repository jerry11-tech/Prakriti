@echo off
REM Quick Start Script for Prakriti AI Facial Analysis System
REM This script starts both Backend and ML Service

title Prakriti AI - Backend & ML Service Launcher
color 0A

echo.
echo ============================================
echo    PRAKRITI AI - FACIAL ANALYSIS SYSTEM
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Python and Node.js found
echo.

REM Install dependencies if needed
echo [1] Installing ML Service dependencies...
cd ml_service
pip install -r requirements.txt >nul 2>&1
cd ..

echo [2] Installing Backend dependencies...
npm install >nul 2>&1

echo.
echo ============================================
echo    STARTING SERVICES
echo ============================================
echo.
echo Starting ML Service on port 5000...
echo Starting Backend on port 3000...
echo.
echo Press Ctrl+C in either window to stop services
echo.

REM Start both services
start "Prakriti ML Service (Port 5000)" cmd /k python ml_service/app.py
timeout /t 2 /nobreak

start "Prakriti Backend (Port 3000)" cmd /k npm start

echo.
echo [OK] Both services should be starting...
echo.
echo Backend:   http://localhost:3000
echo ML Service: http://localhost:5000/health
echo.
pause
