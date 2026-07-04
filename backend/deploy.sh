#!/bin/bash
# ======================================================
# MindShift 后端 - 一键部署脚本
# 适用：任意 Linux VPS（Ubuntu / CentOS / Debian）
# ======================================================
set -e

echo "=========================================="
echo " MindShift API - 服务器部署脚本"
echo "=========================================="

# 1. 安装 Docker
if ! command -v docker &> /dev/null; then
    echo "[1/4] 安装 Docker..."
    curl -fsSL https://get.docker.com | bash
    sudo systemctl enable docker
    sudo systemctl start docker
else
    echo "[1/4] Docker 已安装，跳过"
fi

# 2. 安装 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "[2/4] 安装 Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "[2/4] Docker Compose 已安装，跳过"
fi

# 3. 配置环境变量
echo "[3/4] 配置环境变量..."
if [ ! -f .env ]; then
    cat > .env << 'ENV'
SECRET_KEY=$(openssl rand -hex 32)
AI_API_KEY=your_api_key_here
ENV
    echo "  已生成 .env 文件，请编辑其中的 AI_API_KEY"
else
    echo "  .env 文件已存在，跳过"
fi

# 4. 启动服务
echo "[4/4] 启动服务..."
docker-compose up -d --build

echo ""
echo "=========================================="
echo " 部署完成！"
echo ""
echo "  API 地址: http://$(curl -s ifconfig.me):8000"
echo "  接口文档: http://$(curl -s ifconfig.me):8000/docs"
echo "  管理看板: http://$(curl -s ifconfig.me):8000/admin"
echo ""
echo "  如需配置域名反代，请参考: deploy_nginx.md"
echo "=========================================="
