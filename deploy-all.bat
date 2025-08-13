@echo off
echo ====================================
echo 联锦LED网站一键部署脚本
echo ====================================
echo.
echo 正在同步最新修改到所有平台...
echo.

REM 1. Git同步
echo [1/3] 同步到Git仓库...
git add .
git commit -m "修复管理系统登录问题和功能优化 - %date% %time%"
git push origin master

if %ERRORLEVEL% EQU 0 (
    echo ✅ Git同步成功
) else (
    echo ❌ Git同步失败，请检查网络连接
)

echo.

REM 2. Vercel部署
echo [2/3] 部署到Vercel...
vercel --prod

if %ERRORLEVEL% EQU 0 (
    echo ✅ Vercel部署成功
) else (
    echo ❌ Vercel部署失败，请检查配置
)

echo.

REM 3. 显示部署结果
echo [3/3] 获取部署信息...
vercel ls --limit 1

echo.
echo ====================================
echo 部署完成！
echo ====================================
echo.
echo 您的网站链接：
vercel ls --limit 1 | findstr "https://"
echo.
echo 管理后台登录：
echo 用户名: admin
echo 密码: admin123
echo.
pause
