#!/bin/bash
# Stardew Chat - macOS 打包脚本
# 使用 py2app 打包成 .app

cd "$(dirname "$0")"

echo "=========================================="
echo "  Stardew Chat - 打包 macOS App"
echo "=========================================="
echo

# 检查并创建虚拟环境
if [ ! -d "venv" ]; then
    echo "[INFO] 创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

# 安装依赖
echo "[INFO] 安装依赖..."
pip install -r requirements.txt -q
pip install py2app -q

# 创建 setup.py
cat > setup_mac.py << 'EOF'
from setuptools import setup

APP = ['gui_mac.py']
DATA_FILES = [('templates', ['templates/index.html'])]
OPTIONS = {
    'argv_emulation': False,
    'iconfile': None,
    'plist': {
        'CFBundleName': 'Stardew Chat',
        'CFBundleDisplayName': 'Stardew Chat',
        'CFBundleIdentifier': 'com.aliensweety.stardewchat',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
    },
    'packages': ['flask', 'qrcode', 'PIL'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
EOF

# 打包
echo "[INFO] 打包中..."
python setup_mac.py py2app

echo
echo "=========================================="
echo "  打包完成！"
echo "  App位置: dist/Stardew Chat.app"
echo "=========================================="
