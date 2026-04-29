@echo off
chcp 65001 >nul
title 新生报到系统 - 快速启动

echo ========================================
echo    新生报到系统 - 快速启动
echo ========================================
echo.

echo [1/3] 执行数据库迁移...
"D:\青软\Python\安装\python.exe" manage.py migrate

echo.
echo [2/3] 创建管理员账号...
"D:\青软\Python\安装\python.exe" manage.py createsuperuser_auto

echo.
echo [3/3] 启动服务器...
echo 服务器地址: http://127.0.0.1:8000
echo 管理后台: http://127.0.0.1:8000/admin
echo 接口地址: http://127.0.0.1:8000/api/register/
echo.
"D:\青软\Python\安装\python.exe" manage.py runserver 8000

pause
