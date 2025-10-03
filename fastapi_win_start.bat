@echo off
REM 大麦抢票助手 FastAPI 后端启动脚本

REM 检查是否安装了Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 未找到Python，请先安装Python 3.12或更高版本
    pause
    exit /b 1
)

REM 创建虚拟环境（如果不存在）
if not exist ".venv_fastapi" (
    echo 创建虚拟环境 .venv_fastapi
    python -m venv .venv_fastapi
    if errorlevel 1 (
        echo 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
call ".venv_fastapi\Scripts\activate"
if errorlevel 1 (
    echo 激活虚拟环境失败
    pause
    exit /b 1
)

REM 安装基础FastAPI依赖
pip install -r requirements_fastapi.txt
if errorlevel 1 (
    echo 安装FastAPI依赖失败
    pause
    exit /b 1
)

REM 安装数据库依赖
if exist requirements_db.txt (
    echo 安装数据库依赖
    pip install -r requirements_db.txt
    if errorlevel 1 (
        echo 安装数据库依赖失败
        pause
        exit /b 1
    )
)

REM 提示配置数据库环境变量
if not defined DATABASE_URL (
    echo 注意：未设置DATABASE_URL环境变量，将使用本地默认数据库配置。
    echo 如果需要连接自定义PostgreSQL数据库，请设置DATABASE_URL环境变量。
    echo 详情请查看README_DB.md文件。
    timeout /t 3 >nul
)

REM 启动FastAPI服务器
uvicorn main_fastapi:app --reload --host 0.0.0.0 --port 8000
if errorlevel 1 (
    echo 启动服务器失败
    echo 请检查PostgreSQL服务是否运行及数据库连接配置是否正确
    pause
    exit /b 1
)

REM 保持窗口打开
pause