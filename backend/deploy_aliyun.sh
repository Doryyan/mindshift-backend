#!/bin/bash
# MindShift - 阿里云一键部署脚本
# 使用方法: 上传到服务器后 bash deploy_aliyun.sh

set -e

echo "========================================"
echo " MindShift API - 阿里云部署"
echo "========================================"

# 1. 安装 Docker
if ! command -v docker &> /dev/null; then
    echo "[1/5] 安装 Docker..."
    curl -fsSL https://get.docker.com | bash
    systemctl enable docker
    systemctl start docker
else
    echo "[1/5] Docker 已安装"
fi

# 2. 安装 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "[2/5] 安装 Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# 3. 生成密钥
echo "[3/5] 配置环境变量..."
if [ ! -f .env ]; then
    echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
    echo "AI_API_KEY=" >> .env
fi

# 4. 启动服务
echo "[4/5] 启动后端服务..."
docker-compose up -d --build

echo "[5/5] 配置 Nginx..."

# Nginx 配置
cat > /etc/nginx/sites-enabled/mindshift << 'NGINX'
server {
    listen 8888 ssl;
    server_name _;

    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;

    # API 后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 健康检查
    location /api/v1/health {
        proxy_pass http://127.0.0.1:8000/api/v1/health;
    }

    # 后台看板
    location /admin {
        proxy_pass http://127.0.0.1:8000/admin;
        proxy_set_header Host $host;
    }

    location / {
        return 404;
    }
}
NGINX

# 生成自签名 SSL 证书
mkdir -p /etc/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/server.key \
    -out /etc/nginx/ssl/server.crt \
    -subj "/CN=39.106.98.184" 2>/dev/null

nginx -t && systemctl reload nginx

echo ""
echo "========================================"
echo " 部署完成！"
echo ""
echo "  API:     https://39.106.98.184:8888/api/v1"
echo "  看板:    https://39.106.98.184:8888/admin"
echo "  文档:    https://39.106.98.184:8888/docs"
echo "========================================"
