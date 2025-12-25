@echo off
REM Mental Wellness Companion - Quick Start Script (Windows)

echo ================================================
echo    Mental Wellness Companion
echo    Voice-Based Emotional Support System
echo ================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Installing dependencies (this may take a few minutes)...
    pip install -r requirements.txt
)

REM Check for .env file
if not exist ".env" (
    echo.
    echo WARNING: No .env file found!
    echo Copying .env.example to .env...
    copy .env.example .env
    echo.
    echo Please edit .env and add your API keys:
    echo - ANTHROPIC_API_KEY (required)
    echo - HUME_API_KEY (required)
    echo.
    pause
)

echo.
echo Starting the application...
echo Open http://localhost:8501 in your browser
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the application
python main.py --streamlit

pause
