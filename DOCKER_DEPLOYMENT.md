# Docker 部署指南

本文档详细介绍如何使用 Docker 将 ChemTutor 项目部署到服务器。

**⚠️ 部署前必读（适配 Ubuntu 20.04 + Docker Compose 1.25.0）：**

1. **版本兼容**：docker-compose.yml 使用 `version: '3'` 而非 `3.8`
2. **启动顺序**：分步启动服务，避免 depends_on 问题
3. **RDKit 依赖**：3D_test/Dockerfile 需要额外的系统库（libxrender1、libxext6、libgl1-mesa-glx）
4. **前端构建**：**必须在本地构建**，服务器只托管静态文件，避免内存溢出

## 目录

- [整体架构](#整体架构)
- [准备工作](#准备工作)
- [创建 Docker 配置文件](#创建-docker-配置文件)
- [本地测试](#本地测试)
- [服务器部署](#服务器部署)
- [常见问题](#常见问题)

---

## 整体架构

```
┌─────────────────────────────────────────────────────┐
│                   Nginx (80/443)                     │
│              反向代理 + 静态文件托管                  │
└─────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ ai-chem      │   │ 3d-vis       │   │ image-       │
│ backend      │   │ backend      │   │ identity     │
│ :8000        │   │ :8001        │   │ :8002        │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## 准备工作

### 1. 服务器环境要求

- 操作系统：Linux (Ubuntu 20.04+ 推荐)
- 内存：至少 4GB，推荐 8GB+
- 磁盘：至少 20GB 可用空间
- 网络：开放 80、443 端口

### 2. 检查 Docker 和 Docker Compose 版本

**重要：** 本指南适配 Docker Compose 1.25.0（Ubuntu 20.04 默认版本）

在服务器上执行：

```bash
# 检查版本
docker-compose --version
```

如果版本低于 1.25.0，请升级：
```bash
# 升级 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.25.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. 准备工具

- **XShell** - SSH 连接服务器
- **XFTP** - 上传文件到服务器

---

## 创建 Docker 配置文件

在项目根目录创建以下文件：

### 1. `.env` 环境变量文件

```bash
# GLM API 配置
GLM_API_KEY=your_api_key_here

# 服务端口配置
BACKEND_PORT=8000
FRONTEND_PORT=80
THREE_D_PORT=8001
IMAGE_ID_PORT=8002

# 数据库配置（如果需要）
# DB_HOST=db
# DB_PORT=5432
# DB_NAME=chemtutor
# DB_USER=chemuser
# DB_PASSWORD=your_password
```

### 2. `docker-compose.yml` 编排文件

**⚠️ 重要：兼容 Docker Compose 1.25.0**

```yaml
version: '3'

services:
  # ai_chem 后端服务
  ai-chem-backend:
    build:
      context: ./ai_chem/backend
      dockerfile: Dockerfile
    container_name: ai-chem-backend
    ports:
      - "${BACKEND_PORT}:8000"
    environment:
      - GLM_API_KEY=${GLM_API_KEY}
    volumes:
      - ./ai_chem/backend/data:/app/data
      - ./ai_chem/backend/logs:/app/logs
    restart: unless-stopped
    networks:
      - chem-network

  # 3D 可视化服务
  3d-vis:
    build:
      context: ./3D_test
      dockerfile: Dockerfile
    container_name: 3d-vis-backend
    ports:
      - "${THREE_D_PORT}:8001"
    volumes:
      - ./3D_test/data:/app/data
    restart: unless-stopped
    networks:
      - chem-network

  # 图像识别服务
  image-identity:
    build:
      context: ./image_identity
      dockerfile: Dockerfile
    container_name: image-identity-backend
    ports:
      - "${IMAGE_ID_PORT}:8002"
    volumes:
      - ./image_identity/uploads:/app/uploads
    restart: unless-stopped
    networks:
      - chem-network

  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: chem-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ai_chem/frontend/dist:/usr/share/nginx/html:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    # depends_on 在旧版 Compose 中可能导致启动问题
    # 已移除，启动顺序按需手动控制
    restart: unless-stopped
    networks:
      - chem-network

networks:
  chem-network:
    driver: bridge

volumes:
  chem-data:
  chem-logs:
```

### 3. `ai_chem/backend/Dockerfile`

```dockerfile
# 使用 Python 官方镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要目录
RUN mkdir -p /app/data /app/logs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. 前端构建策略

**⚠️ 重要：本地构建，避免服务器内存溢出**

由于服务器内存有限，**强烈建议在本地构建前端**，而不是在服务器上运行 `npm install`。

**在本地（你的电脑）执行：**
```bash
cd ai_chem/frontend
npm install
npm run build
```

构建完成后，会生成 `ai_chem/frontend/dist` 目录。

**不需要前端 Dockerfile**，Nginx 直接托管这个静态文件夹即可。

### 5. `3D_test/Dockerfile`

**⚠️ 重要：RDKit 需要额外的系统库**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖（RDKit 需要的）
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libboost-dev \
    libxrender1 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

EXPOSE 8001

# 启动命令
CMD ["python", "api.py"]
```

### 6. `image_identity/Dockerfile`

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建上传目录
RUN mkdir -p /app/uploads

EXPOSE 8002

# 启动命令
CMD ["python", "app.py"]
```

### 7. `nginx/nginx.conf`

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    keepalive_timeout 65;
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # 上游服务器定义
    upstream ai_chem_backend {
        server ai-chem-backend:8000;
    }

    upstream three_d_backend {
        server 3d-vis:8001;
    }

    upstream image_identity_backend {
        server image-identity:8002;
    }

    server {
        listen 80;
        server_name your-domain.com;  # 修改为你的域名

        # 前端静态文件
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # ai_chem 后端 API
        location /api/ {
            proxy_pass http://ai_chem_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 3D 可视化 API
        location /3d/ {
            proxy_pass http://three_d_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # 图像识别 API
        location /image/ {
            proxy_pass http://image_identity_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }

    # HTTPS 配置（可选，需要 SSL 证书）
    # server {
    #     listen 443 ssl http2;
    #     server_name your-domain.com;
    #
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #
    #     # ... 其他配置同上
    # }
}
```

### 8. `.dockerignore` 文件

在各个目录创建 `.dockerignore`：

**根目录 `.dockerignore`：**
```
.git
.gitignore
.claude
node_modules
venv
__pycache__
*.pyc
.env
.DS_Store
*.log
```

**ai_chem/backend/.dockerignore：**
```
venv
__pycache__
*.pyc
logs/*
data/.gitkeep
.git
```

---

## 本地测试

### 1. 构建镜像

```bash
# 在项目根目录
docker-compose build
```

### 2. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 测试访问

- 前端：http://localhost
- 后端 API：http://localhost/api/
- API 文档：http://localhost:8000/docs

### 4. 停止服务

```bash
docker-compose down
```

---

## 服务器部署

### 步骤 1：本地构建前端（必须）

**⚠️ 在本地执行，不要在服务器上执行**

```bash
# 进入前端目录
cd ai_chem/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build
```

构建完成后，会生成 `ai_chem/frontend/dist` 目录。

### 步骤 2：准备服务器文件

在本地打包项目文件（已包含前端构建产物）：

```bash
# 排除不必要的文件
tar -czf chemtutor.tar.gz \
  --exclude='node_modules' \
  --exclude='venv' \
  --exclude='.git' \
  --exclude='__pycache__' \
  .
```

### 步骤 3：上传到服务器

**使用 XFTP：**
1. 连接到服务器
2. 创建项目目录：`/opt/chemtutor`
3. 上传 `chemtutor.tar.gz` 到服务器

**使用命令行（可选）：**
```bash
scp chemtutor.tar.gz user@your-server:/opt/chemtutor/
```

### 步骤 4：服务器上解压

使用 XShell 连接到服务器：

```bash
# 进入项目目录
cd /opt/chemtutor

# 解压文件
tar -xzf chemtutor.tar.gz

# 验证前端 dist 目录是否存在
ls -la ai_chem/frontend/dist

# 设置权限
chmod +x docker-compose.yml
```

### 步骤 5：配置环境变量

```bash
# 创建环境变量文件
nano .env
```

输入以下内容：
```bash
# GLM API 配置
GLM_API_KEY=your_api_key_here

# 服务端口配置
BACKEND_PORT=8000
THREE_D_PORT=8001
IMAGE_ID_PORT=8002
```

按 `Ctrl+X`，然后 `Y`，最后 `Enter` 保存。

### 步骤 6：分步启动服务（推荐）

**⚠️ 重要：分步启动，避免 depends_on 问题**

```bash
# 1. 先启动后端服务
docker-compose up -d ai-chem-backend 3d-vis image-identity

# 2. 等待后端服务完全启动（约30-60秒）
sleep 60

# 3. 检查后端服务状态
docker-compose ps

# 4. 确认后端正常运行后，启动 Nginx
docker-compose up -d nginx

# 5. 查看所有服务状态
docker-compose ps
```

### 步骤 7：配置防火墙

```bash
# 开放 HTTP 端口
sudo ufw allow 80/tcp

# 开放 HTTPS 端口（如果使用）
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable
```

### 步骤 8：配置域名（可选）

如果你有域名，将 DNS A 记录指向服务器 IP。

---

## 常见问题

### 1. 端口被占用

```bash
# 查看占用端口的进程
sudo netstat -tulpn | grep :80

# 停止占用端口的进程
sudo kill <PID>
```

### 2. 容器启动失败

```bash
# 查看详细日志
docker-compose logs <service-name>

# 进入容器调试
docker-compose exec <service-name> bash
```

### 3. 内存不足

```bash
# 检查内存使用
free -h

# 在 docker-compose.yml 中限制内存
services:
  ai-chem-backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

### 4. 数据持久化问题

确保 Volume 正确挂载：
```bash
# 查看 volume
docker volume ls

# 备份数据
docker run --rm -v chemtutor_chem-data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data
```

### 5. 更新部署

```bash
# 停止服务
docker-compose down

# 拉取最新代码
git pull

# 重新构建
docker-compose build

# 启动服务
docker-compose up -d
```

---

## 维护命令

```bash
# 查看所有容器
docker ps -a

# 查看容器资源使用
docker stats

# 重启单个服务
docker-compose restart ai-chem-backend

# 清理无用镜像
docker image prune -a

# 查看容器日志
docker logs -f <container-name>

# 进入运行中的容器
docker exec -it <container-name> bash
```

---

## 安全建议

1. **使用非 root 用户运行容器**
2. **配置 HTTPS**（使用 Let's Encrypt 免费证书）
3. **限制 API 访问频率**
4. **定期更新镜像**
5. **备份数据**

---

## SSL 证书配置（可选）

使用 Certbot 获取免费 SSL 证书：

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```
