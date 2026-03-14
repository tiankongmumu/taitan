@echo off
title TITAN Cloud Relay Node (US VPS)
color 0A

echo =====================================================================
echo   TITAN ENGINE - CLOUD RELAY NODE
echo   Starting secure proxy and remote execution API for Titan Brain...
echo =====================================================================
echo.

:: 检查 Python 环境
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    pause
    exit /b
)

:: 环境变量提示区 
:: 如果您没有在 Windows 系统高级设置里配置环境变量，可以在这里临时反注释并写入您的安全密钥
:: set TITAN_RELAY_KEY=titan-vanguard-relay-alpha-99x-CHANGE-THIS-IN-PROD

echo [INFO] Environment ready. Booting up the relay server...
echo [INFO] Press Ctrl+C to stop the server at any time.
echo.

:: 启动 Flask 节点
python cloud_relay_node.py

echo.
echo [WARNING] The Relay Service has stopped!
pause
