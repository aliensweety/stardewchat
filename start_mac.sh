#!/bin/bash
# Stardew Chat - macOS 启动脚本

cd "$(dirname "$0")"

echo "=========================================="
echo "  Stardew Valley Chat Tool - macOS"
echo "=========================================="
echo

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] 请先安装Python3"
    exit 1
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "[INFO] 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "[INFO] 安装依赖..."
pip install -r requirements.txt -q

# 运行服务器
echo "[INFO] 启动服务器..."
python server_cross.py
