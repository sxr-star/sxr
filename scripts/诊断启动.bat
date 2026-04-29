@echo off
chcp 65001 >nul
title 诊断启动问题

echo ========================================
echo    诊断启动问题
echo ========================================
echo.

echo [1/5] 检查 Python 版本...
python --version
if errorlevel 1 (
    echo 错误：Python 未安装或未添加到 PATH
    pause
    exit /b 1
)
echo.

echo [2/5] 检查 Django 安装...
python -c "import django; print('Django 版本:', django.get_version())"
if errorlevel 1 (
    echo 错误：Django 未安装
    echo 正在安装 Django...
    python -m pip install django django-cors-headers
)
echo.

echo [3/5] 检查端口 8000 占用...
netstat -ano | findstr :8000
if errorlevel 1 (
    echo 端口 8000 未被占用
)
echo.

echo [4/5] 检查项目目录...
cd /d "%~dp0.."
echo 当前目录: %CD%
echo.

echo [5/5] 测试 Django 配置...
python manage.py check
if errorlevel 1 (
    echo 错误：Django 配置有问题
)
echo.

echo 诊断完成！
pause