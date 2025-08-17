@echo off
chcp 65001 >nul
echo ========================================
echo 币安强平订单监控系统服务安装
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python环境，请先安装Python 3.8+
    pause
    exit /b 1
)

echo 正在安装NSSM (Non-Sucking Service Manager)...
if not exist "nssm.exe" (
    echo 下载NSSM...
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile 'nssm.zip'"
    powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath '.' -Force"
    move "nssm-2.24\win64\nssm.exe" "nssm.exe"
    rmdir /s /q "nssm-2.24"
    del "nssm.zip"
)

echo 正在注册监控服务...
nssm.exe install "BinanceForceOrderMonitor" "python" "%~dp0forceOrder\main.py"
nssm.exe set "BinanceForceOrderMonitor" AppDirectory "%~dp0forceOrder"
nssm.exe set "BinanceForceOrderMonitor" DisplayName "币安强平订单监控系统"
nssm.exe set "BinanceForceOrderMonitor" Description "监控币安U本位合约强平订单数据"
nssm.exe set "BinanceForceOrderMonitor" Start SERVICE_AUTO_START

echo 服务安装完成！
echo 服务名称: BinanceForceOrderMonitor
echo.
echo 服务管理命令:
echo   启动服务: net start BinanceForceOrderMonitor
echo   停止服务: net stop BinanceForceOrderMonitor
echo   删除服务: nssm.exe remove BinanceForceOrderMonitor confirm
echo.
echo 现在可以启动服务了...
pause 