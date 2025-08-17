@echo off
chcp 65001 >nul
echo ========================================
echo 币安强平订单监控系统
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python环境，请先安装Python 3.8+
    pause
    exit /b 1
)

echo 正在检查依赖包...
pip show websockets >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 依赖包安装失败
        pause
        exit /b 1
    )
)

echo 启动监控系统...
cd forceOrder
python main.py

echo.
echo 监控系统已退出
pause 