#!/bin/bash
# Step 1: 创建 conda 虚拟环境 python3.12 命名为 joker
conda create --name joker python=3.12 -y

# Step 2: 激活虚拟环境
source activate joker

# Step 3: 安装依赖包
pip install -r requirements.txt

# Step 4: 运行 gui.py
python gui.py

# Step 5: 保持命令行窗口打开，直到用户关闭
echo "按Enter键退出..."
read -p ""