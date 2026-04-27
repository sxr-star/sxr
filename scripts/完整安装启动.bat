@echo off
chcp 65001 >nul
title Freshmen Registration System - Setup
setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0.."

echo ========================================
echo    Freshmen Registration System
echo ========================================
echo.

echo [1/6] Installing Django and CORS...
python -m pip install django django-cors-headers -i https://mirrors.aliyun.com/pypi/simple/
echo.

echo [2/6] Running database migrations...
cd /d "%PROJECT_DIR%"
python manage.py migrate
echo.

echo [3/6] Creating api migrations...
python manage.py makemigrations api
echo.

echo [4/6] Applying api migrations...
python manage.py migrate
echo.

echo [5/6] Creating admin account...
python manage.py createsuperuser_auto

echo.
echo ========================================
echo    Admin account created!
echo    Username: admin
echo    Password: admin123
echo ========================================
echo.

echo [6/6] Starting server...
echo Server: http://127.0.0.1:8000
echo Admin: http://127.0.0.1:8000/admin
echo API: http://127.0.0.1:8000/api/register/
echo.
start http://127.0.0.1:8000
python manage.py runserver 8000

pause
