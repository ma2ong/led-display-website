@echo off
echo ====================================
echo 联锦LED管理系统启动脚本
echo ====================================
echo.
echo 正在启动管理系统...
echo.
echo 可用的页面:
echo 1. 测试版登录 (推荐): admin-test.html
echo 2. 标准登录页面: admin-login.html  
echo 3. 完整管理系统: admin-complete-system.html
echo.
echo 默认登录账号: admin / admin123
echo.

REM 启动测试版本
start "" "%~dp0admin-test.html"
echo 测试版本已启动！

echo.
echo 如需启动其他版本，请手动双击对应的HTML文件。
echo.
pause
