@echo off
chcp 65001 >nul
title Install Django
echo Checking Python version...
python --version
echo.
echo Installing Django...
python -m pip install django
echo.
echo Done!
pause
