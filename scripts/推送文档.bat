@echo off
chcp 65001 >nul
title Git Push
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

echo Committing...
git commit -m "Add project documents"
echo.

echo Pushing to GitHub...
git push origin main --force
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
