@echo off
chcp 65001 >nul
color 0A
title 闲鱼掌柜专属 - OpenClaw 激活码生成器

echo =========================================================================
echo       [OpenClaw 闲鱼版] 激活码生成工具 (掌柜自用版，勿外传)
echo =========================================================================
echo.

:INPUT
set /p CLIENT_CODE="请在此粘贴买家发来的机器码: "

if "%CLIENT_CODE%"=="" (
    echo 机器码不能为空！
    goto INPUT
)

set "O1=%CLIENT_CODE:~0,2%"
set "O2=%CLIENT_CODE:~-2%"
set "FINAL_KEY=%O1%CLAW%O2%"

echo.
echo -------------------------------------------------------------------------
echo 🔑 该买家的专属激活码为: 
color 0E
echo %FINAL_KEY%
echo -------------------------------------------------------------------------
echo.
color 0A
echo 可以复制上方金色的激活码发给客户。

pause
echo.
goto INPUT
