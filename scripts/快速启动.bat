@echo off
chcp 65001 >nul
title Freshmen Registration System - Quick Start
setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0.."

echo ========================================
echo    Freshmen Registration System - Quick Start
echo ========================================
echo.

cd /d "%PROJECT_DIR%"

echo [1/3] Running database migrations...
python manage.py migrate

echo.
echo [2/3] Creating admin account...
python manage.py createsuperuser_auto

echo.
echo [3/3] Starting server...
echo Server: http://127.0.0.1:8000
echo Admin: http://127.0.0.1:8000/admin
echo API: http://127.0.0.1:8000/api/register/
echo.
start http://127.0.0.1:8000
python manage.py runserver 8000

pause
