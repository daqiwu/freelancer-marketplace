# AI Security Classifier - Quick Start Guide

## 🚀 快速开始指南

### 一、系统概述

本系统实现了基于AI的安全问题分类功能，可以自动将安全测试问题分类为：
- **SCA (Software Composition Analysis)**: 软件成分分析 - 依赖项漏洞
- **SAST (Static Application Security Testing)**: 静态应用安全测试 - 代码漏洞
- **DAST (Dynamic Application Security Testing)**: 动态应用安全测试 - 运行时漏洞

### 二、环境要求

**后端**:
- Python 3.12+
- MySQL 数据库
- 依赖包见 `backend/requirements.txt`

**前端**:
- Node.js 16+
- Vue 3

### 三、安装步骤

#### 步骤 1: 安装后端依赖

```bash
cd C:\Users\g6316\Desktop\freelancer-marketplace\backend
pip install -r requirements.txt
```

#### 步骤 2: 启动后端服务

```bash
# 使用批处理文件启动 (Windows)
start_backend.bat

# 或手动启动
python -m uvicorn app.main:app --reload --port 8000
```

后端将在 `http://localhost:8000` 运行

#### 步骤 3: 安装前端依赖

```bash
cd C:\Users\g6316\Desktop\ms-FL-frontv3
npm install
```

#### 步骤 4: 启动前端服务

```bash
npm run serve
```

前端将在 `http://localhost:8080` 运行

### 四、访问系统

1. 打开浏览器访问: `http://localhost:8080`
2. 登录系统（使用已有账户）
3. 访问安全分类器: `http://localhost:8080/security`

### 五、快速测试

#### 测试 1: 创建单个安全问题

1. 点击 "Create Issue" 标签
2. 填写表单:
   ```
   标题: CVE-2021-44228 Log4Shell vulnerability in log4j
   描述: Critical remote code execution vulnerability in Apache Log4j. 
         Allows attackers to execute arbitrary code.
   受影响组件: pom.xml - log4j-core 2.14.0
   ```
3. 点击 "Classify with AI"
4. 查看分类结果:
   - 类型: SCA
   - 严重性: CRITICAL
   - 置信度: ~95%
   - 修复建议

#### 测试 2: 批量分类

1. 点击 "Batch Classify" 标签
2. 点击 "Load Example" 加载示例
3. 点击 "Classify Batch"
4. 查看批量分类结果表格

#### 测试 3: 查看统计数据

查看页面顶部的统计仪表板:
- 总问题数
- SCA/SAST/DAST 分布
- 严重性分布

### 六、运行单元测试

```bash
cd C:\Users\g6316\Desktop\freelancer-marketplace\backend

# 运行所有测试
pytest tests/test_security_classifier.py -v

# 运行测试并生成覆盖率报告
pytest tests/test_security_classifier.py -v --cov=app.services.security_classifier_service --cov-report=html

# 查看覆盖率报告
# 打开 backend/htmlcov/index.html
```

### 七、运行 CI 工作流

#### 本地运行 CI 检查

```bash
cd C:\Users\g6316\Desktop\freelancer-marketplace\backend

# 1. 运行代码格式检查
black --check --line-length 120 app/ tests/

# 2. 运行导入排序检查
isort --check-only --profile black --line-length 120 app/ tests/

# 3. 运行代码风格检查
flake8 app/ tests/ --max-line-length=120 --ignore=E203,W503,E501

# 4. 运行安全扫描
bandit -r app/ --exclude '*/tests/*,*/alembic/*' --severity-level medium

# 5. 运行单元测试
pytest tests/ -v --cov=app.services.security_classifier_service --cov-fail-under=80
```

#### GitHub Actions CI

将代码推送到 GitHub 后，CI 工作流会自动运行：

```bash
git add .
git commit -m "feat: Add AI security classifier"
git push origin gaorongrong
```

查看 GitHub Actions 页面查看 CI 结果。

### 八、API 使用示例

#### 使用 cURL 测试 API

```bash
# 1. 获取认证令牌
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'

# 2. 创建安全问题
curl -X POST http://localhost:8000/api/security/issues \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "SQL Injection in login endpoint",
    "description": "User input not sanitized in SQL query",
    "affected_component": "app/auth.py:45"
  }'

# 3. 获取所有问题
curl http://localhost:8000/api/security/issues \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. 获取统计信息
curl http://localhost:8000/api/security/statistics \
  -H "Authorization: Bearer YOUR_TOKEN"

# 5. 批量分类
curl -X POST http://localhost:8000/api/security/batch-classify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "issues": [
      {
        "title": "Outdated package",
        "description": "npm package lodash is outdated",
        "affected_component": "package.json"
      }
    ]
  }'
```

#### 使用 Python 测试

```python
import requests

# 配置
API_URL = "http://localhost:8000/api"
USERNAME = "your_username"
PASSWORD = "your_password"

# 登录
response = requests.post(f"{API_URL}/auth/login", json={
    "username": USERNAME,
    "password": PASSWORD
})
token = response.json()["access_token"]

# 创建安全问题
headers = {"Authorization": f"Bearer {token}"}
issue_data = {
    "title": "XSS vulnerability in user profile",
    "description": "User input not sanitized before rendering",
    "affected_component": "app/templates/profile.html"
}
response = requests.post(
    f"{API_URL}/security/issues",
    json=issue_data,
    headers=headers
)
print(response.json())

# 获取统计信息
response = requests.get(f"{API_URL}/security/statistics", headers=headers)
stats = response.json()
print(f"Total issues: {stats['total']}")
print(f"By type: {stats['by_type']}")
print(f"By severity: {stats['by_severity']}")
```

### 九、分类示例

#### SCA (依赖漏洞) 示例

```json
{
  "title": "CVE-2021-23337 in lodash",
  "description": "The package lodash version 4.17.19 has a known vulnerability. Update to 4.17.21+",
  "affected_component": "package.json"
}
```
**预期结果**: Type=SCA, Severity=HIGH, Confidence>80%

#### SAST (代码漏洞) 示例

```json
{
  "title": "SQL Injection vulnerability detected",
  "description": "Potential SQL injection at line 45. User input concatenated into SQL query",
  "affected_component": "app/services/user_service.py:45"
}
```
**预期结果**: Type=SAST, Severity=HIGH/CRITICAL, Confidence>85%

#### DAST (运行时漏洞) 示例

```json
{
  "title": "Missing security headers",
  "description": "Dynamic scan found missing Content-Security-Policy header on /api/users endpoint",
  "affected_component": "/api/users"
}
```
**预期结果**: Type=DAST, Severity=MEDIUM, Confidence>75%

### 十、常见问题

**Q: 分类结果显示 UNKNOWN 怎么办？**
A: 提供更详细的描述，包含技术术语、错误信息、文件路径等。

**Q: 置信度分数较低怎么办？**
A: 在描述中包含更多具体信息，如 CVE 编号、具体的漏洞类型等。

**Q: 如何提高分类准确性？**
A: 
1. 使用标准的安全术语
2. 包含具体的组件信息（文件路径、包名等）
3. 引用 CVE ID 或其他漏洞标识符
4. 描述漏洞的技术细节

**Q: 数据库连接错误？**
A: 确保 MySQL 服务正在运行，并检查 `app/config.py` 中的数据库配置。

**Q: 前端无法访问 API？**
A: 检查：
1. 后端服务是否运行在 8000 端口
2. CORS 配置是否正确
3. 浏览器控制台的错误信息

### 十一、项目结构

```
freelancer-marketplace/
├── backend/
│   ├── app/
│   │   ├── models/
│   │   │   └── models.py              # 数据模型（包含 SecurityIssue）
│   │   ├── routes/
│   │   │   └── security.py            # API 路由
│   │   ├── services/
│   │   │   └── security_classifier_service.py  # AI 分类服务
│   │   └── main.py                    # 应用入口
│   ├── tests/
│   │   ├── conftest.py                # 测试配置
│   │   └── test_security_classifier.py  # 单元测试
│   ├── pytest.ini                     # Pytest 配置
│   ├── .coveragerc                    # 覆盖率配置
│   └── requirements.txt               # Python 依赖
├── .github/
│   └── workflows/
│       ├── backend-tests.yml          # CI 测试工作流
│       └── backend-sast.yml           # CI 安全扫描工作流
└── AI_SECURITY_CLASSIFIER_README.md   # 详细文档

ms-FL-frontv3/
├── src/
│   ├── views/
│   │   └── SecurityClassifier.vue     # 前端页面
│   └── router/
│       └── index.js                   # 路由配置
```

### 十二、下一步

1. **查看详细文档**: 阅读 `AI_SECURITY_CLASSIFIER_README.md`
2. **运行测试**: 执行单元测试确保系统正常
3. **探索 API**: 使用 Swagger UI (`http://localhost:8000/docs`)
4. **自定义分类**: 根据需求调整分类规则和模板

### 十三、技术支持

- **项目文档**: `AI_SECURITY_CLASSIFIER_README.md`
- **API 文档**: `http://localhost:8000/docs` (Swagger UI)
- **测试覆盖率**: `backend/htmlcov/index.html` (运行测试后生成)

---

**版本**: 1.0.0  
**创建日期**: 2025-10-28  
**作者**: Freelancer Marketplace Team

