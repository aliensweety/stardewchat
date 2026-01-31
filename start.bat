@echo off
cd /d "%~dp0"

echo ==========================================
echo   Stardew Valley Chat Tool
echo ==========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    pause
    exit /b 1
)

if not exist "venv\" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

if not exist "venv\Lib\site-packages\flask\" (
    echo [INFO] Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)

call venv\Scripts\activate.bat
python server.py

pause
