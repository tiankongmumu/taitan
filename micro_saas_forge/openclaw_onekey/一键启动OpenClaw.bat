@echo off
chcp 65001 >nul
color 0B
title OpenClaw (最新版 AI 程序员) 一键安装部署工具 v1.0 - 闲鱼特供版

echo =========================================================================
echo       [OpenClaw AI 程序员] 傻瓜式一键部署工具
echo =========================================================================
echo.
echo 本工具将自动帮你完成:
echo 1. 环境检测 (Docker)
echo 2. 下载 OpenClaw 最新版核心代码
echo 3. 自动配置大模型 API Key 
echo 4. 一键启动并打开控制台
echo.
echo =========================================================================
pause

:: 0. 防倒卖验证 (机器码绑定)
echo.
echo =========================================================================
echo [安全验证] 请输入您的专属激活码
echo =========================================================================
:: 获取 C 盘序列号作为唯一的机器码 (更稳定，不易随网络变动)
FOR /F "tokens=2 delims==" %%A IN ('wmic logicaldisk where "DeviceID='C:'" get VolumeSerialNumber /value') DO SET "MACHINE_CODE=%%A"
:: 简单去短横线 (如果有的话)
SET MACHINE_CODE=%MACHINE_CODE:-=%

echo.
echo 您的专属机器码: %MACHINE_CODE%
echo (如果您还没有激活码，请将此机器码发给闲鱼掌柜获取)

:: 简单的本地哈希对比 (防止同行直接扒走脚本)
:: 激活码算法: 机器码的前两字 + "CLAW" + 机器码的后两字 (这里可以自行修改更复杂的或者接入在线API，本地校验最防呆)
set "EXPECTED_O1=%MACHINE_CODE:~0,2%"
set "EXPECTED_O2=%MACHINE_CODE:~-2%"
set "EXPECTED_KEY=%EXPECTED_O1%CLAW%EXPECTED_O2%"

:INPUT_KEY
set /p USER_KEY="请输入激活码: "

if "%USER_KEY%"=="%EXPECTED_KEY%" (
    echo ✅ 激活成功！欢迎使用本一键部署工具。
    echo activated > .license.key
    goto DOWNLOAD_PAYLOAD
)

if exist ".license.key" (
    echo ✅ ^(检测到已激活授权文件，免密通过^)
    goto DOWNLOAD_PAYLOAD
)

color 0C
echo ❌ 激活码错误！请联系原作者获取正确的卡密。
echo.
goto INPUT_KEY

:DOWNLOAD_PAYLOAD
echo.
echo =========================================================================
echo 📦 正在为您获取【本地部署完整配置包】下载地址...
echo 正在解析防封加密链接...
set "ENCODED_URL=aHR0cHM6Ly9wYW4uYmFpZHUuY29tL3MvMXFnWkRSUndLT1FjOF9qVjQzUWJuWUE/cHdkPXl6czc="
powershell -Command "$url = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('%ENCODED_URL%')); Set-Clipboard -Value $url; Start-Process $url"
echo ✅ 解析成功！已自动使用默认浏览器打开下载链接。
echo ^(备用：如果没打开，链接已经复制到了您的【剪贴板】，您可以直接去浏览器粘贴^)
echo 提示：等配置包下载完成后，请将配置包解压到当前目录再继续。
echo =========================================================================
pause

rem 1. 环境检测
echo.
echo [1/4] 正在检测运行环境...
docker --version >nul 2>&1
if "%errorlevel%" NEQ "0" (
    color 0C
    echo ❌ 未检测到 Docker Desktop!
    echo OpenClaw 需要依赖 Docker 运行。
    echo 请先去官网下载并安装 Docker Desktop ^(安装后需要重启电脑^):
    echo 下载地址: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit
)
echo ✅ Docker 环境检测通过!

rem 2. 下载代码 
echo.
echo [2/4] 正在准备 OpenClaw 核心文件...
if not exist "openclaw" (
    echo 正在从国内加速镜像库拉取最新代码 ^(防 404/超时^)...
    git clone https://kkgithub.com/openclaw/openclaw.git
    if "%errorlevel%" NEQ "0" (
        color 0C
        echo ❌ 代码下载失败，请检查网络^(建议开启加速器或更换热点^)后重试。
        pause
        exit
    )
) else (
    echo ✅ 检测到已存在 OpenClaw 文件夹，跳过下载。
)

cd openclaw

rem 3. 配置环境变量
echo.
echo [3/4] 正在配置大语言模型 API 密钥...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
    ) else (
        echo OPENAI_API_KEY=> .env
    )
    
    echo.
    echo ⚠️ 首次运行需要配置你的模型 Key。
    echo 推荐使用 OpenAI API Key ^(sk-...^)
    set /p API_KEY="请输入你的 API Key (右键粘贴): "
    
    echo. >> .env
    echo OPENAI_API_KEY=%API_KEY% >> .env
    echo WORKSPACE_MOUNT_PATH=%cd%\workspace >> .env
    
    echo ✅ 配置文件 .env 创建成功!
) else (
    echo ✅ 检测到 .env 配置文件已存在，跳过配置步骤。
    echo 如需修改 Key，请记事本打开 openclaw 目录下的 .env 文件。
)

rem 4. 启动容器
echo.
echo [4/4] 正在拉取镜像并启动容器 ^(首次运行可能需要 5-15 分钟下载几GB依赖，请耐心等待^)...
echo.
docker compose up -d

if "%errorlevel%" NEQ "0" (
    color 0C
    echo.
    echo ❌ 启动或拉取镜像失败！
    echo 这通常是因为国内网络无法直连 Docker Hub。
    echo 请检查:
    echo 1. Docker Desktop 软件是否已经打开并运行在后台
    echo 2. 你是否配置了国内镜像源 ^(如 阿里云、网易等^) 或开启了正确的代理。
    echo 教程说明附带了【网易、阿里云镜像源】的配置截图，请参考教程修改 Docker 设置后重试。
    echo.
    pause
    exit
)

echo.
color 0A
echo =========================================================================
echo 🎉 部署成功！
echo =========================================================================
echo OpenClaw 服务已在后台运行。
echo 正在为你自动打开浏览器控制台...
echo.
echo ⚠️ 提示: 如果打不开或者白屏，请等待 1-2 分钟让容器完全启动即可刷新页面。
echo 停止服务方法: 在当前弹出的黑框里按 Ctrl+C，或者关掉本窗口后运行 stop.bat
echo =========================================================================

timeout /t 3 >nul
start http://localhost:3000
pause
