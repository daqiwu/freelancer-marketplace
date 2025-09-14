# 用户模块测试文档

## 概述

本目录包含用户模块的完整测试套件，包括模型测试、服务层测试和路由层测试。

## 测试结构

```
app/test/user_test/
├── __init__.py          # 测试模块初始化
├── model_test.py        # 用户模型测试
├── service_test.py      # 用户服务层测试
└── route_test.py        # 用户路由层测试
```

## 测试类型

### 1. 模型测试 (model_test.py)
- 测试User、UserCreate、UserLogin等模型的创建和验证
- 测试字段约束和数据类型
- 测试JSON序列化功能

### 2. 服务层测试 (service_test.py)
- 测试用户注册功能
- 测试用户登录功能
- 测试各种异常情况处理
- 使用Mock模拟数据库操作

### 3. 路由层测试 (route_test.py)
- 测试HTTP端点响应
- 测试请求验证
- 测试错误处理
- 使用TestClient进行集成测试

## 运行测试

### 安装测试依赖
```bash
pip install pytest pytest-asyncio httpx
```

### 运行所有用户测试
```bash
pytest app/test/user_test/ -v
```

### 运行特定测试文件
```bash
# 运行模型测试
pytest app/test/user_test/model_test.py -v

# 运行服务层测试
pytest app/test/user_test/service_test.py -v

# 运行路由层测试
pytest app/test/user_test/route_test.py -v
```

### 运行特定测试方法
```bash
pytest app/test/user_test/service_test.py::TestUserServices::test_user_register_success -v
```

## 测试覆盖的功能

### 用户注册
- ✅ 成功注册新用户
- ✅ 邮箱已存在时的错误处理
- ✅ 用户名已存在时的错误处理
- ✅ 数据验证错误处理

### 用户登录
- ✅ 成功登录
- ✅ 用户不存在的错误处理
- ✅ 密码错误的错误处理
- ✅ 数据验证错误处理

### 模型验证
- ✅ 字段类型验证
- ✅ 字段长度限制
- ✅ 必填字段验证
- ✅ JSON序列化

## 测试最佳实践

1. **隔离性**: 每个测试都是独立的，不依赖其他测试
2. **Mock使用**: 使用Mock对象模拟外部依赖（如数据库）
3. **异常测试**: 测试各种异常情况的处理
4. **数据验证**: 测试输入数据的验证逻辑
5. **覆盖率**: 覆盖所有主要功能和边界情况

## 注意事项

- 测试使用Mock对象，不需要真实的数据库连接
- 异步测试使用pytest-asyncio插件
- 路由测试使用FastAPI的TestClient
- 所有测试都包含中文注释，便于理解
