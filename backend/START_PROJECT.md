# 前后端项目启动指南

## 📁 项目路径
- **后端**: `C:\Users\g6316\Desktop\freelancer-marketplace\backend`
- **前端**: `C:\Users\g6316\Desktop\ms-FL-frontv2`

---

## 🚀 启动步骤

### 第一步：启动数据库（Docker）

**打开终端 1** (项目根目录):
```cmd
cd C:\Users\g6316\Desktop\freelancer-marketplace

# 启动 MySQL 数据库
docker-compose up -d db

# 查看数据库状态
docker ps

# 查看数据库日志（确认启动成功）
docker logs freelancer-mysql
```

等待看到 `ready for connections` 信息。

---

### 第二步：启动后端服务

**打开终端 2** (后端目录):
```cmd
cd C:\Users\g6316\Desktop\freelancer-marketplace\backend

# 激活虚拟环境
.venv\Scripts\activate

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**成功标志**：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**验证后端**：
- 访问 API 文档: http://localhost:8000/docs
- 测试健康检查: http://localhost:8000/api/v1/auth/me（应该返回 401）

---

### 第三步：配置前端 API 地址

**在前端项目中修改 API 配置**：

找到前端项目的 API 配置文件（通常是 `src/api/auth.js` 或类似文件）：

**需要修改的地方**：
```javascript
// 修改前（原AWS地址）
const API_BASE_URL = 'http://a12345.amazonaws.com/api/v1'

// 修改后（本地后端）
const API_BASE_URL = 'http://localhost:8000/api/v1'
```

或者使用环境变量（推荐）：

创建 `ms-FL-frontv2/.env.development` 文件：
```env
VUE_APP_API_BASE_URL=http://localhost:8000/api/v1
```

然后在代码中使用：
```javascript
const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000/api/v1'
```

---

### 第四步：启动前端服务

**打开终端 3** (前端目录):
```cmd
cd C:\Users\g6316\Desktop\ms-FL-frontv2

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run serve
```

**成功标志**：
```
App running at:
- Local:   http://localhost:8080/
- Network: http://192.168.x.x:8080/
```

---

## ✅ 验证项目运行

### 1. 检查所有服务状态

在浏览器中打开以下地址：

| 服务 | 地址 | 预期结果 |
|------|------|----------|
| 数据库 | - | `docker ps` 显示 `freelancer-mysql` 运行中 |
| 后端 API 文档 | http://localhost:8000/docs | 显示 Swagger UI |
| 前端应用 | http://localhost:8080 | 显示前端页面 |

### 2. 测试完整流程

1. **打开前端**: http://localhost:8080
2. **注册新用户**（客户）
3. **登录**
4. **检查浏览器控制台**（F12）:
   - Network 标签应该显示请求到 `http://localhost:8000/api/v1/...`
   - 没有 CORS 错误
   - 请求成功返回 200

---

## 🔧 常见问题

### 问题 1: 前端无法连接后端

**症状**: 浏览器控制台显示网络错误

**检查**:
```cmd
# 1. 确认后端正在运行
curl http://localhost:8000/docs

# 2. 检查前端 API_BASE_URL 配置
# 打开浏览器控制台，查看请求地址

# 3. 检查 CORS（后端已配置，应该没问题）
```

### 问题 2: 后端启动失败

**症状**: `ModuleNotFoundError` 或其他导入错误

**解决**:
```cmd
cd C:\Users\g6316\Desktop\freelancer-marketplace\backend

# 确认虚拟环境已激活
.venv\Scripts\activate

# 重新安装依赖
pip install -r requirements.txt

# 如果还有问题，重建虚拟环境
deactivate
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 问题 3: 数据库连接失败

**症状**: 后端启动时报数据库连接错误

**解决**:
```cmd
# 1. 检查数据库是否运行
docker ps

# 2. 如果没有，启动数据库
docker-compose up -d db

# 3. 等待 30 秒让数据库完全启动
timeout /t 30

# 4. 测试连接
docker exec -it freelancer-mysql mysql -ufreelancer -ppassword123 -e "SHOW DATABASES;"
```

### 问题 4: 端口被占用

**症状**: `Address already in use`

**解决**:
```cmd
# 查看占用端口的进程
# 后端端口 8000
netstat -ano | findstr :8000

# 前端端口 8080
netstat -ano | findstr :8080

# 杀死进程（替换 PID）
taskkill /F /PID <进程ID>

# 或者使用不同的端口
# 后端: uvicorn app.main:app --reload --port 8001
# 前端: npm run serve -- --port 8081
```

---

## 📝 快速启动脚本

### Windows 批处理脚本

创建 `start_all.bat` 在项目根目录：

```batch
@echo off
echo ========================================
echo   启动完整项目
echo ========================================

echo 1. 启动数据库...
start "数据库" cmd /k "docker-compose up db"
timeout /t 10

echo 2. 启动后端...
start "后端" cmd /k "cd backend && .venv\Scripts\activate && uvicorn app.main:app --reload"
timeout /t 5

echo 3. 启动前端...
start "前端" cmd /k "cd ..\ms-FL-frontv2 && npm run serve"

echo.
echo ========================================
echo   所有服务已启动！
echo ========================================
echo   数据库: localhost:3306
echo   后端: http://localhost:8000
echo   前端: http://localhost:8080
echo ========================================
```

---

## 🎯 开发工作流

### 日常开发流程

1. **早上开始工作**:
   ```cmd
   # 终端 1: 启动数据库
   docker-compose up -d db
   
   # 终端 2: 启动后端
   cd backend
   .venv\Scripts\activate
   uvicorn app.main:app --reload
   
   # 终端 3: 启动前端
   cd ..\ms-FL-frontv2
   npm run serve
   ```

2. **修改代码**: 
   - 后端代码修改会自动重载（`--reload`）
   - 前端代码修改会自动热更新

3. **测试**: 
   - 访问 http://localhost:8080 测试功能
   - 查看 http://localhost:8000/docs 测试 API

4. **下班关闭**:
   ```cmd
   # 按 Ctrl+C 停止后端和前端
   
   # 停止数据库（可选）
   docker-compose down
   ```

---

## 📊 端口使用情况

| 服务 | 端口 | 说明 |
|------|------|------|
| MySQL 数据库 | 3306 | Docker 容器 |
| 后端 API | 8000 | FastAPI + Uvicorn |
| 前端开发服务器 | 8080 | Vue CLI / npm |

---

## 🔐 默认账户

系统预设管理员账户：
```
邮箱: admin@freelancer-platform.com
密码: AdminSecure2024!
角色: 管理员
```

---

## 📚 相关文档

- `DATABASE_SETUP_GUIDE.md` - 数据库建表指南
- `QUICK_START.md` - API 测试指南
- `MIGRATION_CHANGES.md` - 代码变更说明

---

## 🆘 需要帮助？

如遇到问题：
1. 检查浏览器控制台（F12）的错误信息
2. 查看后端终端的日志输出
3. 查看前端终端的编译错误
4. 检查 Docker 日志：`docker logs freelancer-mysql`

