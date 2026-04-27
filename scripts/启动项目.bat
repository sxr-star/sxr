@echo off
chcp 65001 >nul
title Freshmen Registration System - Start Project
setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0.."

cd /d "%PROJECT_DIR%"

echo Installing Django...
python -m pip install django django-cors-headers
echo.
echo Database setup...
python manage.py migrate
echo.
echo Creating admin account...
python manage.py createsuperuser
echo.
echo Starting server...
echo Server: http://127.0.0.1:8000
echo Admin: http://127.0.0.1:8000/admin
echo.
start http://127.0.0.1:8000
python manage.py runserver 8000
