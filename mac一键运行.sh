#!/bin/bash
# 大麦抢票助手 GUI版启动脚本（macOS版）

# 设置变量
VENV_NAME=".venv_gui"
PYTHON_VERSION="3.12"

# 检查是否安装了Python
echo "检查Python版本..."
if ! command -v python$PYTHON_VERSION &> /dev/null; then
    # 尝试使用python3命令
    if ! command -v python3 &> /dev/null; then
        echo "未找到Python，请先安装Python 3.12或更高版本。"
        echo "推荐从官网 https://www.python.org/downloads/macos/ 下载安装。"
        exit 1
    else
        PYTHON="python3"
        echo "使用已安装的Python 3版本。"
    fi
else
    PYTHON="python$PYTHON_VERSION"
fi

# 检查ChromeDriver是否存在
if [ ! -f "chromedriver.exe" ]; then
    echo "未找到chromedriver.exe文件，尝试查找macOS版本..."
    if [ ! -f "chromedriver" ]; then
        echo "警告：未找到ChromeDriver，请下载与您的Chrome浏览器版本匹配的macOS版ChromeDriver。"
        echo "下载地址：https://chromedriver.chromium.org/downloads"
        echo "下载后请重命名为chromedriver并放在项目根目录下。"
        read -p "是否继续？(y/n) " choice
        if [[ $choice != [Yy]* ]]; then
            exit 1
        fi
    fi
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "$VENV_NAME" ]; then
    echo "创建虚拟环境 $VENV_NAME..."
    $PYTHON -m venv $VENV_NAME
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

# 安装项目依赖
echo "安装项目依赖..."
pip install -r requirements.txt --upgrade
if [ $? -ne 0 ]; then
    echo "安装依赖失败"
    exit 1
fi

# 授予执行权限给启动脚本
chmod +x $0

# 启动GUI应用
echo "启动大麦抢票助手GUI..."
if ! $PYTHON GUI.py; then
    echo "GUI启动失败"
    echo "请检查依赖安装是否完整或查看错误日志以获取更多信息"
    read -p "按回车键退出..."
    exit 1
fi

echo "\n应用已关闭\n"