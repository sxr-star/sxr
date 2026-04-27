@echo off
title Git Push
echo ========================================
echo    Git Push Script
echo ========================================
echo.

cd /d "D:\Freshmen Registration Program\Version\Version 1.0"

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
