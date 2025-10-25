@echo off
REM ========================================
REM 后端快速启动脚本
REM ========================================

echo =========================================
echo   启动后端服务
echo =========================================
echo.

REM 检查是否在 backend 目录
if not exist "app\main.py" (
    echo [错误] 请在 backend 目录下运行此脚本
    pause
    exit /b 1
)

echo 步骤 1: 检查虚拟环境...
if not exist ".venv" (
    echo [错误] 虚拟环境不存在
    echo 请先运行: python -m venv .venv
    pause
    exit /b 1
)
echo [OK] 虚拟环境存在

echo.
echo 步骤 2: 激活虚拟环境...
call .venv\Scripts\activate.bat
echo [OK] 虚拟环境已激活

echo.
echo 步骤 3: 检查数据库连接...
docker ps | findstr freelancer-mysql >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 数据库未运行，尝试启动...
    cd ..
    docker-compose up -d db
    cd backend
    echo 等待数据库启动（20秒）...
    timeout /t 20 /nobreak
)
echo [OK] 数据库正在运行

echo.
echo 步骤 4: 启动后端服务...
echo.
echo =========================================
echo   后端服务启动中...
echo   访问: http://localhost:8000/docs
echo   按 Ctrl+C 停止服务
echo =========================================
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

