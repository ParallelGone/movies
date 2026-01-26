@echo off
REM =========================================
REM Toronto Rep Cinema Calendar - Auto Deploy
REM =========================================

echo.
echo ========================================
echo TORONTO REP CINEMA CALENDAR
echo Auto-Update and Deploy to GitHub
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Starting automated deployment...
echo.

REM Run the deployment script
python deploy.py

REM Check if deployment was successful
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS! Calendar deployed to GitHub
    echo ========================================
    echo.
    echo Your calendar should be live in 2-3 minutes at:
    echo https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/
    echo.
) else (
    echo.
    echo ========================================
    echo DEPLOYMENT FAILED
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause
