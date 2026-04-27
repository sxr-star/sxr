@echo off
chcp 65001 >nul
title 新生报到系统 - 自动安装脚本
setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0.."

echo ========================================
echo    新生报到系统 - 安装和启动脚本
echo ========================================
echo.

echo [1/6] 安装 Django 和 CORS 扩展...
python -m pip install django django-cors-headers -i https://mirrors.aliyun.com/pypi/simple/
echo.

echo [2/6] 执行数据库迁移...
cd /d "%PROJECT_DIR%"
python manage.py migrate
echo.

echo [3/6] 创建 api 应用迁移文件...
python manage.py makemigrations api
echo.

echo [4/6] 执行 api 应用迁移...
python manage.py migrate
echo.

echo [5/6] 创建管理员账号...
python manage.py createsuperuser_auto

echo.
echo ========================================
echo    管理员账号已创建！
echo    用户名: admin
echo    密码: admin123
echo ========================================
echo.

echo [6/6] 启动服务器...
echo 服务器启动后，在浏览器访问: http://127.0.0.1:8000
echo 接口地址: http://127.0.0.1:8000/api/register/
echo.
start http://127.0.0.1:8000
python manage.py runserver 8000

pause
