@echo off
echo ========================================
echo   CodeBuddy LED 管理系统快速启动
echo ========================================
echo.
echo 正在启动管理后台登录页面...
echo.

REM 尝试多种方式打开管理登录页面
echo [1] 尝试使用默认浏览器打开...
start "" "admin-login.html"

timeout /t 2 > nul

echo [2] 如果上面的方式不工作，请手动操作：
echo     - 双击 admin-login.html 文件
echo     - 或在浏览器中打开该文件
echo.
echo ========================================
echo   登录信息
echo ========================================
echo 用户名: admin
echo 密码:   admin123
echo ========================================
echo.

REM 等待用户输入
echo 按任意键继续...
pause > nul

REM 显示更多信息
echo.
echo ========================================
echo   如果遇到问题，请尝试以下方法：
echo ========================================
echo.
echo 方法1: 双击 admin-login.html 文件
echo 方法2: 右键 admin-login.html -> 打开方式 -> 浏览器
echo 方法3: 在浏览器地址栏输入完整路径：
echo        file:///%~dp0admin-login.html
echo.
echo 方法4: 启动本地服务器：
echo        python -m http.server 8000
echo        然后访问: http://localhost:8000/admin-login.html
echo.

echo 按任意键退出...
pause > nul
