@echo off
chcp 65001 >nul
title 新生报到系统 - 安装诊断

set PYTHON=D:\青软\Python\python安装路径\python.exe
set PROJECT=D:\青软\Freshmen Registration Program\Version\Version 1.0

echo ========================================
echo    新生报到系统 - 安装诊断
echo ========================================
echo.

echo [步骤1] 检查 Python...
"%PYTHON%" --version
echo.

echo [步骤2] 安装 pip（使用 ensurepip）...
"%PYTHON%" -m ensurepip --upgrade
echo.

echo [步骤3] 安装 Django...
"%PYTHON%" -m pip install django
echo.

echo [步骤4] 进入项目目录并执行数据库迁移...
cd /d "%PROJECT%"
"%PYTHON%" manage.py migrate
echo.

echo [步骤5] 创建管理员账号...
"%PYTHON%" manage.py createsuperuser_auto
echo.

echo ========================================
echo    启动服务器...
echo ========================================
echo 服务器地址: http://127.0.0.1:8000
echo.
"%PYTHON%" manage.py runserver 8000
