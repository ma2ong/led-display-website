@echo off
chcp 65001 >nul
title 联锦LED管理系统启动器

echo.
echo ========================================
echo    联锦LED显示屏管理系统启动器
echo    Complete Chinese LED Admin System
echo ========================================
echo.

cd /d "%~dp0"

echo 正在启动管理系统...
echo.

python start_admin_system.py

pause