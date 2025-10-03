#!/bin/bash
# 大麦抢票助手 FastAPI 后端启动脚本

# 设置变量
VENV_NAME=".venv_fastapi"
PYTHON_VERSION="3.12"
PORT="8000"

# 检查是否安装了Python
echo "检查Python版本..."
if ! command -v python$PYTHON_VERSION &> /dev/null; then
    echo "未找到Python $PYTHON_VERSION，请先安装"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "$VENV_NAME" ]; then
    echo "创建虚拟环境 $VENV_NAME..."
    python$PYTHON_VERSION -m venv $VENV_NAME
    if [ $? -ne 0 ]; then
        echo "创建虚拟环境失败"
        exit 1
    fi
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source $VENV_NAME/bin/activate
if [ $? -ne 0 ]; then
    echo "激活虚拟环境失败"
    exit 1
fi

# 安装或更新FastAPI依赖
echo "安装FastAPI依赖..."
pip install -r requirements_fastapi.txt --upgrade
if [ $? -ne 0 ]; then
    echo "安装FastAPI依赖失败"
    exit 1
fi

# 安装数据库依赖
echo "安装数据库依赖..."
pip install -r requirements_db.txt --upgrade
if [ $? -ne 0 ]; then
    echo "安装数据库依赖失败"
    exit 1
fi

# 提示配置数据库环境变量
if [ -z "$DATABASE_URL" ]; then
    echo "注意：未设置DATABASE_URL环境变量，将使用本地默认数据库配置。"
    echo "如果需要连接自定义PostgreSQL数据库，请设置环境变量："
    echo "  export DATABASE_URL=postgresql://username:password@host:port/database"
    echo "详情请查看README_DB.md文件。"
    sleep 3
fi

# 授予执行权限给启动脚本
chmod +x $0

# 启动FastAPI服务器
echo "启动FastAPI服务器（端口 $PORT）..."
echo "服务器启动后，可访问以下地址："
echo "- API文档：http://localhost:$PORT/docs"
echo "- Redoc文档：http://localhost:$PORT/redoc"
echo "- WebSocket端点：ws://localhost:$PORT/ws/task/{task_id}"

echo "正在启动服务器..."
if ! uvicorn main_fastapi:app --reload --host 0.0.0.0 --port $PORT; then
    echo "服务器启动失败"
    echo "请检查PostgreSQL服务是否运行及数据库连接配置是否正确"
    echo "可以查看README_DB.md获取更多帮助"
    exit 1
fi
echo "\n按Ctrl+C停止服务器\n"

uvicorn main_fastapi:app --reload --host 0.0.0.0 --port $PORT
if [ $? -ne 0 ]; then
    echo "启动服务器失败"
    exit 1
fi