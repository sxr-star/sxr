@echo off
title Git Push Script
setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0.."

echo ========================================
echo    Git Push Script
echo ========================================
echo.

cd /d "%PROJECT_DIR%"

echo Adding files...
git add .
echo.

echo Please enter commit message (press Enter for default):
set /p commit_msg=
if "%commit_msg%"=="" set commit_msg=Update code

echo Committing...
git commit -m "%commit_msg%"
echo.

echo Pushing to GitHub...
git push origin main
echo.

if %errorlevel%==0 (
    echo ========================================
    echo    Push Successful!
    echo ========================================
) else (
    echo ========================================
    echo    Push Failed, please check network
    echo ========================================
)

pause
