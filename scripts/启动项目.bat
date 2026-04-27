@echo off
title 新生报到系统 - 启动项目
setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0.."

cd /d "%PROJECT_DIR%"

echo 正在安装 Django...
python -m pip install django django-cors-headers
echo.
echo 安装完成！现在创建数据库...
python manage.py migrate
echo.
echo 正在创建管理员账号...
python manage.py createsuperuser
echo.
echo 启动服务器...
python manage.py runserver 8000
pause
