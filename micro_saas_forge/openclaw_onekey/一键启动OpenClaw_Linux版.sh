#!/bin/bash
# 一键启动 OpenClaw (Linux 专用版)

echo "========================================================================="
echo "      [OpenClaw AI 程序员] 傻瓜式一键部署工具 (Linux版)"
echo "========================================================================="

echo ""
echo "========================================================================="
echo "[安全验证] 请输入您的专属激活码"
echo "========================================================================="

# 提取 Linux 机器特征作为机器码
MACHINE_CODE=$(cat /etc/machine-id 2>/dev/null)
if [ -z "$MACHINE_CODE" ]; then
    MACHINE_CODE=$(head -c 16 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -n 16)
fi

echo ""
echo "您的专属机器码: $MACHINE_CODE"
echo "(如果您还没有激活码，请将此机器码发给闲鱼掌柜获取)"

# 本地算法校验
O1=${MACHINE_CODE:0:2}
O2=${MACHINE_CODE: -2}
EXPECTED_KEY="${O1}CLAW${O2}"

read -p "请输入激活码: " USER_KEY

if [ "$USER_KEY" == "$EXPECTED_KEY" ]; then
    echo "✅ 激活成功！"
    echo "activated" > .license.key
else
    if [ -f ".license.key" ]; then
        echo "✅ (检测到已激活授权文件，免密通过)"
    else
        echo "❌ 激活码错误！请联系原作者获取正确的卡密。"
        exit 1
    fi
fi

echo ""
echo "========================================================================="
echo "📦 正在为您获取【本地部署完整配置包】下载地址..."
echo "正在解析防封加密链接..."
ENCODED_URL="aHR0cHM6Ly9wYW4uYmFpZHUuY29tL3MvMXFnWkRSUndLT1FjOF9qVjQzUWJuWUE/cHdkPXl6czc="
DECODED_URL=$(echo "$ENCODED_URL" | base64 -d)
echo ""
echo "==== 你的专属下载链接 ===="
echo "$DECODED_URL"
echo "========================="
if command -v xdg-open &> /dev/null; then
    xdg-open "$DECODED_URL" &>/dev/null &
fi
echo "待提速辅助包下载完成后再继续执行本脚本"
echo "========================================================================="
read -p "按回车键继续..."

# 1. 环境检测
echo ""
echo "[1/4] 正在检测运行环境..."
if ! command -v docker &> /dev/null; then
    echo "❌ 未检测到 Docker!"
    echo "请先使用您的包管理器 (如 apt/yum) 安装 Docker 及 Docker Compose。"
    exit 1
fi
echo "✅ Docker 环境检测通过!"

# 2. 下载代码 
echo ""
echo "[2/4] 正在准备 OpenClaw 核心文件..."
if [ ! -d "openclaw" ]; then
    echo "正在从国内加速镜像库拉取最新代码 (防 404/超时)..."
    git clone https://kkgithub.com/openclaw/openclaw.git
    if [ $? -ne 0 ]; then
        echo "❌ 代码下载失败，请检查网络。"
        exit 1
    fi
else
    echo "✅ 检测到已存在 OpenClaw 文件夹，跳过下载。"
fi

cd openclaw

# 3. 配置环境变量
echo ""
echo "[3/4] 正在配置大语言模型 API 密钥..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
    else
        touch .env
    fi
    echo "⚠️ 首次运行需要配置你的模型 Key。"
    read -p "请输入您的 API Key (回车确认): " API_KEY
    echo "OPENAI_API_KEY=$API_KEY" >> .env
    echo "WORKSPACE_MOUNT_PATH=$(pwd)/workspace" >> .env
    echo "✅ 配置文件 .env 创建成功!"
fi

# 4. 启动容器
echo ""
echo "[4/4] 正在拉取镜像并启动容器 (首次运行可能需要 5-15 分钟下载几GB依赖，请耐心等待)..."
docker compose up -d

if [ $? -ne 0 ]; then
    echo "❌ 启动失败！请检查 Docker 服务是否运行，以及是否配置了国内镜像源。"
    exit 1
fi

echo "========================================================================="
echo "🎉 部署成功！"
echo "OpenClaw 服务已在后台运行。"
echo "请在浏览器访问: http://localhost:3000"
echo "========================================================================="
