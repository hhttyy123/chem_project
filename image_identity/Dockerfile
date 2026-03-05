# Image Identity - 化学分子图像识别服务
FROM python:3.10-slim

WORKDIR /app

# 使用阿里云 Debian 镜像源 (避免官方源同步问题)
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 安装系统依赖 (RDKit 和 DECIMER 需要)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libboost-dev \
    libboost-python-dev \
    libxrender1 \
    libxext6 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY app.py .
COPY identify.py .
COPY outputImage.py .
COPY templates/ ./templates/
COPY static/ ./static/

# 创建上传目录
RUN mkdir -p uploads static/outputs

# 配置 pip 国内镜像源 (清华大学)
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 Python 依赖 (DECIMER, RDKit, Flask, Pillow)
RUN pip install --no-cache-dir \
    Flask \
    Pillow \
    rdkit \
    decimer

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# 启动命令
CMD ["python", "app.py"]
