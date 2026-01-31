@echo off
cd /d "%~dp0"

echo ==========================================
echo   Stardew Chat - 打包EXE
echo ==========================================
echo.

REM 激活虚拟环境
if not exist "venv\" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

REM 安装依赖
echo [INFO] Installing dependencies...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [INFO] Building EXE...
pyinstaller --noconfirm --onefile --windowed ^
    --name "StardewChat" ^
    --add-data "templates;templates" ^
    gui.py

echo.
echo ==========================================
echo   打包完成！
echo   EXE文件位置: dist\StardewChat.exe
echo ==========================================

pause
