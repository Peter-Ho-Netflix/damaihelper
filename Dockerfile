# 使用官方Python基础镜像
FROM python:3.12-slim-buster

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建虚拟环境
RUN python -m venv /app/.venv

# 复制requirements文件
COPY requirements_fastapi.txt requirements_db.txt /app/

# 安装Python依赖
RUN pip install --upgrade pip && \
    pip install -r requirements_fastapi.txt -r requirements_db.txt

# 复制项目代码
COPY . /app/

# 暴露FastAPI端口
EXPOSE 8000

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/ || exit 1

# 运行FastAPI应用
CMD ["uvicorn", "main_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]