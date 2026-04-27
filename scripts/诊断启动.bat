@echo off
chcp 65001 >nul
title 新生报到系统 - 安装诊断
setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0.."

echo ========================================
echo    新生报到系统 - 安装诊断
echo ========================================
echo.

echo [步骤1] 检查 Python...
python --version
echo.

echo [步骤2] 安装 pip（使用 ensurepip）...
python -m ensurepip --upgrade
echo.

echo [步骤3] 安装 Django...
python -m pip install django
echo.

echo [步骤4] 进入项目目录并执行数据库迁移...
cd /d "%PROJECT_DIR%"
python manage.py migrate
echo.

echo [步骤5] 创建管理员账号...
python manage.py createsuperuser_auto
echo.

echo ========================================
echo    启动服务器...
echo ========================================
echo 服务器地址: http://127.0.0.1:8000
echo.
start http://127.0.0.1:8000
python manage.py runserver 8000
