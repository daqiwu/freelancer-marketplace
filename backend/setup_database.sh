#!/bin/bash

# ========================================
# 数据库快速建表脚本 (Linux/Mac)
# ========================================

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "  数据库建表向导"
echo "========================================="
echo ""

# 检查是否在 backend 目录
if [ ! -f "app/main.py" ]; then
    echo -e "${RED}[错误] 请在 backend 目录下运行此脚本${NC}"
    echo "当前目录: $(pwd)"
    exit 1
fi

echo "步骤 1: 检查 .env 文件..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}[提示] 未找到 .env 文件，正在创建...${NC}"
    cat > .env << EOF
# 数据库配置
USE_DOCKER=true
DOCKER_DATABASE_URL=mysql+aiomysql://freelancer:password123@db:3306/freelancer_marketplace

# JWT 配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
    echo -e "${GREEN}[OK] .env 文件已创建${NC}"
else
    echo -e "${GREEN}[OK] .env 文件已存在${NC}"
fi

echo ""
echo "步骤 2: 启动 Docker 数据库..."
cd ..
docker-compose up -d db
if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] Docker 启动失败，请检查 Docker 是否安装并运行${NC}"
    exit 1
fi
echo -e "${GREEN}[OK] Docker 数据库已启动${NC}"

echo ""
echo "步骤 3: 等待 MySQL 启动..."
echo "等待 30 秒让 MySQL 完全启动..."
sleep 30

echo ""
echo "步骤 4: 检查 Python 依赖..."
cd backend
if ! pip show aiomysql > /dev/null 2>&1; then
    echo -e "${YELLOW}[提示] 安装 Python 依赖...${NC}"
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}[错误] 依赖安装失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK] 依赖已安装${NC}"
else
    echo -e "${GREEN}[OK] 依赖已安装${NC}"
fi

echo ""
echo "步骤 5: 初始化数据库..."
python init_db.py
if [ $? -ne 0 ]; then
    echo -e "${RED}[错误] 数据库初始化失败${NC}"
    exit 1
fi

echo ""
echo "========================================="
echo "  数据库建表完成！"
echo "========================================="
echo ""
echo "预设管理员账户："
echo "  用户名: system_admin"
echo "  邮箱: admin@freelancer-platform.com"
echo "  密码: AdminSecure2024!"
echo ""
echo "下一步："
echo "  1. 启动后端: uvicorn app.main:app --reload"
echo "  2. 访问 API 文档: http://localhost:8000/docs"
echo "  3. 使用管理员账户登录测试"
echo ""
echo "查看更多信息: DATABASE_SETUP_GUIDE.md"
echo ""

