@echo off
REM Sapphire Application Launcher
REM This file automatically installs dependencies and launches the application

echo Welcome to Sapphire!
echo.

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found in the system.
    echo Please install Python 3.8 or higher from python.org
    echo.
    pause
    exit /b 1
)

REM Navigate to script directory
cd /d "%~dp0"

REM Check for pip
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: pip not found.
    echo Please reinstall Python with pip included.
    echo.
    pause
    exit /b 1
)

REM Check for requirements.txt file
if not exist "requirements\requirements.txt" (
    echo Error: requirements\requirements.txt file not found.
    echo Make sure all project files are in the correct locations.
    echo.
    pause
    exit /b 1
)

REM Install dependencies
echo Checking and installing dependencies...
python -m pip install -r requirements\requirements.txt --user --quiet

REM Launch application
echo Starting Sapphire...
echo.
python source\sapphire.py

REM If an error occurred, show it
if %errorlevel% neq 0 (
    echo.
    echo An error occurred while starting the application.
    echo Error code: %errorlevel%
    echo.
    pause
)
