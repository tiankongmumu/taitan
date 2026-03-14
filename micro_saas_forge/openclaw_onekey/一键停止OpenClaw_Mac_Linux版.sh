#!/bin/bash
# 一键关闭 OpenClaw (Mac/Linux 通用)

echo "========================================================================="
echo "      正在停止 OpenClaw 后台服务..."
echo "========================================================================="
echo ""

if [ -d "openclaw" ]; then
    cd openclaw
    docker compose down
    
    if [ $? -ne 0 ]; then
        echo "❌ 停止失败！请确保 Docker 软件正在运行。"
    else
        echo "✅ OpenClaw 服务已成功停止并卸载容器。"
    fi
else
    echo "⚠️ 未检测到 OpenClaw 文件夹，服务可能尚未安装。"
fi

echo ""
