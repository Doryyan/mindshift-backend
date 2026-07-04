# MindShift API - Nginx 反代配置指南

## 适用场景
你已经有一台服务器和一个已备案域名，希望通过 `https://www.hcjworld.com/admin` 访问看板。

## 前提条件
1. 服务器已安装 Docker + Docker Compose
2. 域名 hcjworld.com 已解析到服务器 IP
3. 已安装 Nginx 和 SSL 证书（推荐使用 certbot）

## 部署步骤

### 1. 上传代码到服务器
```bash
# 在你的本地电脑上
cd /Users/nannan/NLP 语言教练_Codex
tar czf mindshift-backend.tar.gz backend/
scp mindshift-backend.tar.gz root@你的服务器IP:/root/
ssh root@你的服务器IP
```

### 2. 在服务器上解压并启动
```bash
tar xzf mindshift-backend.tar.gz
cd backend

# 可选：编辑 .env 配置
nano .env

# 启动服务
./deploy.sh
```

### 3. 配置 Nginx 反代

创建网站配置文件 `/etc/nginx/sites-available/hcjworld.com`：

```nginx
server {
    listen 80;
    server_name www.hcjworld.com hcjworld.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name www.hcjworld.com hcjworld.com;

    ssl_certificate /etc/letsencrypt/live/www.hcjworld.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/www.hcjworld.com/privkey.pem;

    # 后台管理看板（带密码保护）
    location /admin {
        # 密码保护（可选）
        auth_basic "Admin Area";
        auth_basic_user_file /etc/nginx/.htpasswd;

        proxy_pass http://127.0.0.1:8000/admin;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API 文档（可选：仅供内网访问）
    location /docs {
        allow 127.0.0.1;
        deny all;
        proxy_pass http://127.0.0.1:8000/docs;
    }

    # 健康检查
    location /api/v1/health {
        proxy_pass http://127.0.0.1:8000/api/v1/health;
    }
}
```

### 4. 设置密码保护

```bash
# 安装 htpasswd
sudo apt install apache2-utils -y

# 创建管理员账号
sudo htpasswd -c /etc/nginx/.htpasswd admin
# 输入两次密码

# 启用配置
sudo ln -sf /etc/nginx/sites-available/hcjworld.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. 申请 SSL 证书
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d www.hcjworld.com -d hcjworld.com
```

### 6. 访问看板

打开浏览器访问：**https://www.hcjworld.com/admin**

输入第 4 步设置的管理员账号密码即可。

## 替代方案：无密码保护
如果你不需要密码，删掉 Nginx 配置中的 `auth_basic` 相关行即可。
但强烈建议至少设置密码保护，毕竟后台数据敏感。
