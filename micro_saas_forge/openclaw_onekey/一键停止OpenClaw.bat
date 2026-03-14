@echo off
chcp 65001 >nul
color 0B
title OpenClaw 服务停止工具

echo =========================================================================
echo       正在停止 OpenClaw 后台服务...
echo =========================================================================
echo.

if exist "openclaw" (
    cd openclaw
    docker compose down
    
    if %errorlevel% neq 0 (
        color 0C
        echo ❌ 停止失败！请确保 Docker Desktop 正在运行。
    ) else (
        color 0A
        echo ✅ OpenClaw 服务已成功停止并卸载容器。
    )
) else (
    color 0E
    echo ⚠️ 未检测到 OpenClaw 文件夹，服务可能尚未安装或您在错误的目录运行了脚本。
)

echo.
pause
