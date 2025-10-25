@echo off
REM ========================================
REM 数据库快速建表脚本 (Windows)
REM ========================================

echo =========================================
echo   数据库建表向导
echo =========================================
echo.

REM 检查是否在 backend 目录
if not exist "app\main.py" (
    echo [错误] 请在 backend 目录下运行此脚本
    echo 当前目录: %CD%
    pause
    exit /b 1
)

echo 步骤 1: 检查 .env 文件...
if not exist ".env" (
    echo [提示] 未找到 .env 文件，正在创建...
    echo # 数据库配置 > .env
    echo USE_DOCKER=true >> .env
    echo DOCKER_DATABASE_URL=mysql+aiomysql://freelancer:password123@db:3306/freelancer_marketplace >> .env
    echo. >> .env
    echo # JWT 配置 >> .env
    echo SECRET_KEY=your-secret-key-change-in-production >> .env
    echo [OK] .env 文件已创建
) else (
    echo [OK] .env 文件已存在
)

echo.
echo 步骤 2: 启动 Docker 数据库...
cd ..
docker-compose up -d db
if %errorlevel% neq 0 (
    echo [错误] Docker 启动失败，请检查 Docker 是否安装并运行
    pause
    exit /b 1
)
echo [OK] Docker 数据库已启动

echo.
echo 步骤 3: 等待 MySQL 启动...
echo 等待 30 秒让 MySQL 完全启动...
timeout /t 30 /nobreak

echo.
echo 步骤 4: 检查 Python 依赖...
cd backend
pip show aiomysql >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 安装 Python 依赖...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
    echo [OK] 依赖已安装
) else (
    echo [OK] 依赖已安装
)

echo.
echo 步骤 5: 初始化数据库...
python init_db.py
if %errorlevel% neq 0 (
    echo [错误] 数据库初始化失败
    pause
    exit /b 1
)

echo.
echo =========================================
echo   数据库建表完成！
echo =========================================
echo.
echo 预设管理员账户：
echo   用户名: system_admin
echo   邮箱: admin@freelancer-platform.com
echo   密码: AdminSecure2024!
echo.
echo 下一步：
echo   1. 启动后端: uvicorn app.main:app --reload
echo   2. 访问 API 文档: http://localhost:8000/docs
echo   3. 使用管理员账户登录测试
echo.
echo 查看更多信息: DATABASE_SETUP_GUIDE.md
echo.
pause

