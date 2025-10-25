# 数据库建表完整指南

## 📋 目录
1. [使用 Docker 数据库（推荐）](#方案1-使用-docker-数据库推荐)
2. [使用本地 MySQL](#方案2-使用本地-mysql)
3. [常见问题排查](#常见问题排查)

---

## 方案1: 使用 Docker 数据库（推荐）

### 步骤 1: 创建 .env 配置文件

在 `backend` 目录下创建 `.env` 文件：

```bash
cd backend
copy .env.example .env
```

或手动创建 `backend/.env` 文件，内容如下：

```env
# 使用 Docker 数据库
USE_DOCKER=true
DOCKER_DATABASE_URL=mysql+aiomysql://freelancer:password123@db:3306/freelancer_marketplace

# JWT 配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 步骤 2: 启动 Docker 数据库

在项目根目录执行：

```bash
# 启动 MySQL 数据库容器
docker-compose up -d db

# 查看容器状态
docker ps
```

等待几秒让 MySQL 完全启动。

### 步骤 3: 验证数据库连接

```bash
# 测试连接到 MySQL
docker exec -it freelancer-mysql mysql -ufreelancer -ppassword123 freelancer_marketplace

# 成功连接后，输入以下命令查看数据库
SHOW DATABASES;

# 退出 MySQL
exit
```

### 步骤 4: 安装 Python 依赖

```bash
cd backend

# 使用 pip 安装
pip install -r requirements.txt

# 或使用 poetry（如果有）
poetry install
```

### 步骤 5: 运行数据库初始化脚本

```bash
# 在 backend 目录下执行
python init_db.py
```

**预期输出**：
```
CREATE TABLE roles ...
CREATE TABLE users ...
CREATE TABLE orders ...
CREATE TABLE payments ...
CREATE TABLE reviews ...
CREATE TABLE customer_inbox ...
CREATE TABLE provider_inbox ...

✅ 预设管理员账户创建成功！
   用户名: system_admin
   邮箱: admin@freelancer-platform.com
   密码: AdminSecure2024!
   角色: 管理员

数据库初始化完成
```

### 步骤 6: 验证数据表是否创建成功

```bash
# 进入 MySQL 容器
docker exec -it freelancer-mysql mysql -ufreelancer -ppassword123 freelancer_marketplace

# 查看所有表
SHOW TABLES;

# 查看表结构
DESC users;
DESC orders;
DESC payments;

# 查看角色数据
SELECT * FROM roles;

# 查看管理员账户
SELECT id, username, email, role_id FROM users;

# 退出
exit
```

**预期看到的表**：
- `roles` - 角色表
- `users` - 用户表
- `customer_profiles` - 客户资料表
- `provider_profiles` - 服务商资料表
- `orders` - 订单表
- `payments` - 支付记录表
- `reviews` - 评价表
- `customer_inbox` - 客户通知表
- `provider_inbox` - 服务商通知表

### 步骤 7: 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档。

---

## 方案2: 使用本地 MySQL

如果你已经安装了本地 MySQL，可以按以下步骤操作：

### 步骤 1: 创建数据库

```bash
# 登录 MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE freelancer_marketplace CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建用户
CREATE USER 'freelancer'@'localhost' IDENTIFIED BY 'password123';

# 授权
GRANT ALL PRIVILEGES ON freelancer_marketplace.* TO 'freelancer'@'localhost';
FLUSH PRIVILEGES;

# 退出
exit
```

### 步骤 2: 配置 .env 文件

创建 `backend/.env` 文件：

```env
# 使用本地数据库
USE_DOCKER=false
LOCAL_DATABASE_URL=mysql+aiomysql://freelancer:password123@localhost:3306/freelancer_marketplace

# JWT 配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 步骤 3: 安装依赖并初始化

```bash
cd backend
pip install -r requirements.txt
python init_db.py
```

### 步骤 4: 验证

```bash
mysql -ufreelancer -ppassword123 freelancer_marketplace

SHOW TABLES;
SELECT * FROM roles;
exit
```

---

## 使用 Alembic 进行数据库迁移（可选）

如果你想使用 Alembic 管理数据库迁移：

### 初始化 Alembic（如果还没有）

```bash
cd backend
alembic init alembic
```

### 配置 Alembic

编辑 `alembic.ini`，修改：
```ini
sqlalchemy.url = mysql+aiomysql://freelancer:password123@localhost:3306/freelancer_marketplace
```

### 创建迁移

```bash
# 自动生成迁移文件
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

### 查看迁移历史

```bash
alembic history
alembic current
```

---

## 常见问题排查

### 问题 1: `ModuleNotFoundError: No module named 'aiomysql'`

**解决方案**：
```bash
pip install aiomysql
# 或
pip install -r requirements.txt
```

### 问题 2: Docker 容器无法连接

**解决方案**：
```bash
# 检查容器状态
docker ps -a

# 查看容器日志
docker logs freelancer-mysql

# 重启容器
docker-compose restart db

# 等待 MySQL 完全启动（约 30 秒）
docker logs -f freelancer-mysql
```

### 问题 3: `Access denied for user`

**原因**: 数据库用户名或密码不匹配

**解决方案**：
- 检查 `.env` 文件中的数据库 URL
- 检查 `docker-compose.yml` 中的环境变量
- 确保用户名、密码一致

**Docker 配置**:
```yaml
MYSQL_USER: freelancer
MYSQL_PASSWORD: password123
MYSQL_DATABASE: freelancer_marketplace
```

**对应的 DATABASE_URL**:
```
mysql+aiomysql://freelancer:password123@db:3306/freelancer_marketplace
```

### 问题 4: `sqlalchemy.exc.OperationalError: (2003, "Can't connect to MySQL server")`

**原因**: 数据库服务未启动或主机名错误

**解决方案**：
```bash
# Docker 模式: 确保使用主机名 'db'
DOCKER_DATABASE_URL=mysql+aiomysql://freelancer:password123@db:3306/freelancer_marketplace

# 本地模式: 使用 'localhost'
LOCAL_DATABASE_URL=mysql+aiomysql://freelancer:password123@localhost:3306/freelancer_marketplace
```

### 问题 5: 表已存在错误

**解决方案**：
```bash
# 进入数据库
mysql -ufreelancer -ppassword123 freelancer_marketplace

# 删除所有表（谨慎操作！）
DROP DATABASE freelancer_marketplace;
CREATE DATABASE freelancer_marketplace CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 重新初始化
python init_db.py
```

### 问题 6: 字符编码问题

**解决方案**：
确保数据库使用 UTF-8 编码：
```sql
ALTER DATABASE freelancer_marketplace CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 验证清单

完成后，请确认：

- [ ] Docker 容器正在运行（`docker ps` 可以看到 `freelancer-mysql`）
- [ ] `.env` 文件已创建且配置正确
- [ ] Python 依赖已安装（`pip list | grep aiomysql`）
- [ ] `init_db.py` 执行成功
- [ ] 数据库中有 9 张表
- [ ] 角色表有 3 条记录（customer, provider, admin）
- [ ] 用户表有 1 条管理员记录
- [ ] 后端服务可以启动（`uvicorn app.main:app --reload`）
- [ ] API 文档可访问（http://localhost:8000/docs）

---

## 快速命令参考

### Docker 模式

```bash
# 1. 启动数据库
docker-compose up -d db

# 2. 等待启动（查看日志）
docker logs -f freelancer-mysql
# 看到 "ready for connections" 即可 Ctrl+C

# 3. 初始化数据库
cd backend
pip install -r requirements.txt
python init_db.py

# 4. 启动后端
uvicorn app.main:app --reload

# 5. 查看数据库
docker exec -it freelancer-mysql mysql -ufreelancer -ppassword123 freelancer_marketplace
```

### 本地 MySQL 模式

```bash
# 1. 创建数据库
mysql -u root -p
CREATE DATABASE freelancer_marketplace;
CREATE USER 'freelancer'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON freelancer_marketplace.* TO 'freelancer'@'localhost';
exit

# 2. 配置 .env
USE_DOCKER=false
LOCAL_DATABASE_URL=mysql+aiomysql://freelancer:password123@localhost:3306/freelancer_marketplace

# 3. 初始化
cd backend
pip install -r requirements.txt
python init_db.py

# 4. 启动后端
uvicorn app.main:app --reload
```

---

## 下一步

数据库建表完成后：

1. ✅ 测试 API 端点（http://localhost:8000/docs）
2. ✅ 使用预设管理员账户登录
3. ✅ 注册测试用户（客户、服务商）
4. ✅ 测试完整的订单流程
5. ✅ 连接前端项目

---

## 预设账户信息

数据库初始化后会自动创建管理员账户：

```
用户名: system_admin
邮箱: admin@freelancer-platform.com
密码: AdminSecure2024!
角色: 管理员 (role_id=3)
```

**重要**: 生产环境部署时请修改默认密码！

---

需要帮助？请查看：
- `QUICK_START.md` - 快速开始指南
- `MIGRATION_CHANGES.md` - 数据库变更说明
- `MONOLITH_MIGRATION_COMPLETE_GUIDE.md` - 完整技术文档

