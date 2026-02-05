@echo off
REM Start Velma - NDIS Virtual AI Executive Suite
REM This script starts the Velma API server with frontend

echo.
echo 🚀 Starting Velma - NDIS Virtual AI Executive Suite
echo ==================================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ⚠️  Virtual environment not found. Creating...
    python -m venv venv
)

REM Activate virtual environment
echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
if not exist "venv\.dependencies_installed" (
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
    echo. > venv\.dependencies_installed
) else (
    echo ✅ Dependencies already installed
)

REM Check if .env exists
if not exist ".env" (
    echo ⚙️  Creating .env from example...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your API keys and configuration
    echo    Press Enter when ready...
    pause
)

REM Start the server
echo.
echo 🌟 Starting Velma API Server...
echo.
echo    Frontend: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo    Health:   http://localhost:8000/health
echo.
echo Press Ctrl+C to stop the server
echo ==================================================
echo.

python scripts\run_api.py
