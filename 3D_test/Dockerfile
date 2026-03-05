# MolVis 3D Backend - 分子结构解析服务
FROM python:3.10-slim

WORKDIR /app

# 使用阿里云 Debian 镜像源 (避免官方源同步问题)
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装系统依赖 (RDKit 和科学计算库需要)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libboost-dev \
    libboost-python-dev \
    libboost-system-dev \
    libxrender1 \
    libxext6 \
    libgl1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 配置 pip 国内镜像源 (清华大学)
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 Python 依赖
# 注意：RDKit 安装时间较长，请耐心等待
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY api.py .
COPY data/ ./data/

# 暴露端口
EXPOSE 8001

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

# 启动命令
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]
