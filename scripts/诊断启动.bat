@echo off
chcp 65001 >nul
title Freshmen Registration System - Diagnosis
setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0.."

echo ========================================
echo    Freshmen Registration System - Diagnosis
echo ========================================
echo.

echo [Step 1] Checking Python...
python --version
echo.

echo [Step 2] Installing pip...
python -m ensurepip --upgrade
echo.

echo [Step 3] Installing Django...
python -m pip install django
echo.

echo [Step 4] Running database migrations...
cd /d "%PROJECT_DIR%"
python manage.py migrate
echo.

echo [Step 5] Creating admin account...
python manage.py createsuperuser_auto
echo.

echo ========================================
echo    Starting server...
echo ========================================
echo Server: http://127.0.0.1:8000
echo.
start http://127.0.0.1:8000
python manage.py runserver 8000
