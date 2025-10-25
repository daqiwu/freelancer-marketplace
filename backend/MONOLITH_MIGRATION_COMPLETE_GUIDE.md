# 微服务转单体架构 - 完整技术文档

## 📋 文档概述

本文档提供完整的系统功能、API、数据库结构说明，用于将微服务架构迁移到单体架构（Monolith）。

**版本**: v1.1 (基于微服务版本)  
**更新日期**: 2025-10-24  
**目标**: 提供足够详细的技术规格，以便从零开始实现功能相同的单体应用

---

## 🎯 系统概述

### 业务领域
自由职业者服务平台 (Freelancer Service Platform)

### 核心功能
1. **用户认证** - 注册、登录、JWT认证
2. **用户资料** - 客户资料、服务商资料管理
3. **订单管理** - 发布、接单、审核、状态流转
4. **支付系统** - 模拟支付功能
5. **评价系统** - 订单评价、评分统计
6. **通知系统** - 业务事件通知

### 用户角色
- **Customer (客户)** - role_id = 1
- **Provider (服务商)** - role_id = 2  
- **Admin (管理员)** - role_id = 3

---

## 🗄️ 数据库设计

### MySQL 数据库

#### 1. users 表 (用户账号)

```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username),
    FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**字段说明**:
- `id`: 用户唯一标识 (BIGINT 自增)
- `username`: 用户名 (唯一，索引)
- `email`: 邮箱 (唯一，索引，用于登录)
- `password_hash`: bcrypt加密的密码
- `role_id`: 角色ID (1=Customer, 2=Provider, 3=Admin)
- `created_at/updated_at`: 时间戳

**密码加密**: 使用 bcrypt 算法，成本因子默认12

---

#### 2. roles 表 (角色定义)

```sql
CREATE TABLE roles (
    id INT PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO roles (id, role_name, description) VALUES
(1, 'customer', '客户 - 可以发布订单'),
(2, 'provider', '服务商 - 可以接单提供服务'),
(3, 'admin', '管理员 - 可以审核订单和管理系统');
```

---

#### 3. orders 表 (订单信息)

```sql
CREATE TABLE orders (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    provider_id BIGINT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    service_type ENUM(
        'cleaning_repair',
        'it_technology', 
        'education_training',
        'life_health',
        'design_consulting',
        'other'
    ) NOT NULL,
    status ENUM(
        'pending_review',
        'pending',
        'accepted',
        'in_progress',
        'completed',
        'cancelled'
    ) DEFAULT 'pending_review' NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    location ENUM('NORTH', 'SOUTH', 'EAST', 'WEST', 'MID') NOT NULL,
    address VARCHAR(255),
    service_start_time DATETIME,
    service_end_time DATETIME,
    payment_status ENUM('unpaid', 'paid') DEFAULT 'unpaid' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_customer_id (customer_id),
    INDEX idx_provider_id (provider_id),
    INDEX idx_status (status),
    INDEX idx_service_type (service_type),
    INDEX idx_location (location)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**字段详解**:
- `customer_id`: 客户ID (外键关联users.id)
- `provider_id`: 服务商ID (接单后设置，外键关联users.id)
- `service_type`: 服务类型枚举
- `status`: 订单状态 (默认pending_review)
- `payment_status`: 支付状态
- `service_start_time/service_end_time`: 服务时间范围

**订单状态流转**:
```
pending_review (待审核)
    ↓ (管理员批准)
pending (待接单)
    ↓ (服务商接单)
accepted (已接单)
    ↓ (服务进行中)
in_progress (进行中)
    ↓ (服务完成)
completed (已完成)
    ↓ (客户支付)
[payment_status: unpaid → paid]

任何状态都可以 → cancelled (已取消)
```

**业务规则**:
- 只有pending_review订单可以被管理员审核
- 只有pending订单可以被服务商接单
- 只有completed订单可以支付
- 只有paid订单可以评价

---

#### 4. payments 表 (支付记录)

```sql
CREATE TABLE payments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE,
    customer_id BIGINT NOT NULL,
    provider_id BIGINT,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('simulated') DEFAULT 'simulated',
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    transaction_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_order_id (order_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_provider_id (provider_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

**说明**:
- 每个订单只能有一条支付记录 (order_id UNIQUE)
- payment_method固定为'simulated' (模拟支付)
- transaction_id使用UUID生成

---

### MongoDB 数据库

#### 1. customer_profiles 集合 (客户资料)

```javascript
{
  "user_id": 1,                    // 关联users.id (唯一索引)
  "location": "NORTH",             // ENUM: NORTH, SOUTH, EAST, WEST, MID
  "address": "北京市朝阳区XX路XX号",
  "budget_preference": 1000.0,     // 预算偏好
  "created_at": ISODate("2025-10-24T10:00:00Z"),
  "updated_at": ISODate("2025-10-24T10:00:00Z")
}

// 索引
db.customer_profiles.createIndex({ "user_id": 1 }, { unique: true })
```

**业务规则**:
- 一个user_id只能有一个客户资料
- 只有role_id=1的用户可以创建客户资料

---

#### 2. provider_profiles 集合 (服务商资料)

```javascript
{
  "user_id": 2,                    // 关联users.id (唯一索引)
  "skills": ["Python", "FastAPI"], // 技能列表
  "experience_years": 5,           // 工作年限
  "hourly_rate": 50.0,            // 时薪
  "availability": "Full-time",     // 可用性描述
  "portfolio": [                   // 作品集URLs
    "https://example.com/project1"
  ],
  "rating": 4.8,                   // 平均评分 (默认5.0)
  "total_reviews": 20,             // 评价总数 (默认0)
  "created_at": ISODate("2025-10-24T10:00:00Z"),
  "updated_at": ISODate("2025-10-24T10:00:00Z")
}

// 索引
db.provider_profiles.createIndex({ "user_id": 1 }, { unique: true })
```

**业务规则**:
- 一个user_id只能有一个服务商资料
- 只有role_id=2的用户可以创建服务商资料
- rating和total_reviews由评价系统自动更新

---

#### 3. reviews 集合 (订单评价)

```javascript
{
  "order_id": 123,                 // 订单ID (唯一索引)
  "customer_id": 1,                // 客户ID
  "provider_id": 2,                // 服务商ID
  "stars": 5,                      // 评分 (1-5)
  "content": "服务非常好",          // 评价内容
  "created_at": ISODate("2025-10-24T10:00:00Z")
}

// 索引
db.reviews.createIndex({ "order_id": 1 }, { unique: true })
db.reviews.createIndex({ "provider_id": 1 })
db.reviews.createIndex({ "customer_id": 1 })
```

**业务规则**:
- 一个订单只能评价一次
- 只有订单状态为paid才能评价
- 评分范围: 1-5星
- 创建评价后自动更新provider_profiles的rating和total_reviews

---

#### 4. customer_inbox 集合 (客户通知)

```javascript
{
  "customer_id": 1,                // 客户ID
  "order_id": 123,                 // 相关订单ID
  "message": "您的订单已被接受",    // 通知消息
  "is_read": false,                // 是否已读
  "created_at": ISODate("2025-10-24T10:00:00Z")
}

// 索引
db.customer_inbox.createIndex({ "customer_id": 1, "created_at": -1 })
db.customer_inbox.createIndex({ "is_read": 1 })
```

---

#### 5. provider_inbox 集合 (服务商通知)

```javascript
{
  "provider_id": 2,                // 服务商ID
  "order_id": 123,                 // 相关订单ID
  "message": "您成功接受了订单",    // 通知消息
  "is_read": false,                // 是否已读
  "created_at": ISODate("2025-10-24T10:00:00Z")
}

// 索引
db.provider_inbox.createIndex({ "provider_id": 1, "created_at": -1 })
db.provider_inbox.createIndex({ "is_read": 1 })
```

---

## 🔌 完整 API 规格

### 基础信息
- **API前缀**: `/api/v1`
- **认证方式**: JWT Bearer Token
- **Token有效期**: 30分钟
- **限流**: 60次/分钟

### JWT Token结构
```json
{
  "sub": "1",           // user_id (字符串)
  "role": 1,            // role_id
  "exp": 1697564400     // 过期时间
}
```

### 通用响应格式
成功响应 (200):
```json
{
  "data": { ... },
  "message": "success"
}
```

错误响应 (4xx/5xx):
```json
{
  "detail": "错误描述"
}
```

---

## 1. 认证服务 API

### 1.1 用户注册
```
POST /api/v1/auth/register
```

**请求体**:
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "role_id": 1
}
```

**验证规则**:
- username: 非空，唯一
- email: 邮箱格式，唯一
- password: 非空
- role_id: 1, 2, 或 3

**响应** (200):
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
```

**业务逻辑**:
1. 验证email格式和唯一性
2. 验证username唯一性
3. 使用bcrypt加密密码 (cost=12)
4. 插入users表
5. 返回用户基本信息

**错误响应**:
- 400: 用户名或邮箱已存在

---

### 1.2 用户登录
```
POST /api/v1/auth/login
```

**请求体**:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**响应** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**业务逻辑**:
1. 根据email查询用户
2. 验证密码 (bcrypt.checkpw)
3. 生成JWT Token (sub=user_id, role=role_id, exp=30分钟)
4. 返回token

**错误响应**:
- 401: 邮箱或密码错误

---

### 1.3 获取当前用户信息
```
GET /api/v1/auth/me
Headers: Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role_id": 1
}
```

**业务逻辑**:
1. 从JWT token解析user_id
2. 查询users表返回用户信息

---

## 2. 用户资料 API

### 2.1 创建客户资料
```
POST /api/v1/customer/profile
Headers: Authorization: Bearer <token>
```

**请求体**:
```json
{
  "location": "NORTH",
  "address": "北京市朝阳区XX路",
  "budget_preference": 1000.0
}
```

**验证规则**:
- location: NORTH, SOUTH, EAST, WEST, MID
- budget_preference: >= 0
- 只有role_id=1的用户可以创建

**响应** (200):
```json
{
  "user_id": 1,
  "location": "NORTH",
  "address": "北京市朝阳区XX路",
  "budget_preference": 1000.0,
  "created_at": "2025-10-24T10:00:00Z",
  "updated_at": "2025-10-24T10:00:00Z"
}
```

**业务逻辑**:
1. 验证用户role_id=1
2. 检查是否已存在资料
3. 插入MongoDB customer_profiles集合
4. 返回创建的资料

**错误响应**:
- 403: 非客户角色
- 400: 资料已存在

---

### 2.2 获取客户资料
```
GET /api/v1/customer/profile
Headers: Authorization: Bearer <token>
```

**响应** (200): 同创建响应

---

### 2.3 更新客户资料
```
PUT /api/v1/customer/profile
Headers: Authorization: Bearer <token>
```

**请求体** (部分更新):
```json
{
  "address": "新地址",
  "budget_preference": 1500.0
}
```

**响应** (200): 更新后的完整资料

---

### 2.4 创建服务商资料
```
POST /api/v1/provider/profile
Headers: Authorization: Bearer <token>
```

**请求体**:
```json
{
  "skills": ["Python", "FastAPI"],
  "experience_years": 5,
  "hourly_rate": 50.0,
  "availability": "Full-time",
  "portfolio": ["https://example.com/project1"]
}
```

**验证规则**:
- skills: 数组
- experience_years: >= 0
- hourly_rate: >= 0
- 只有role_id=2的用户可以创建

**响应** (200):
```json
{
  "user_id": 2,
  "skills": ["Python", "FastAPI"],
  "experience_years": 5,
  "hourly_rate": 50.0,
  "availability": "Full-time",
  "portfolio": ["https://example.com/project1"],
  "rating": 5.0,
  "total_reviews": 0,
  "created_at": "2025-10-24T10:00:00Z",
  "updated_at": "2025-10-24T10:00:00Z"
}
```

---

### 2.5 获取服务商资料 / 更新服务商资料
```
GET /api/v1/provider/profile
PUT /api/v1/provider/profile
Headers: Authorization: Bearer <token>
```

类似客户资料的GET/PUT操作

---

## 3. 订单管理 API

### 3.1 客户发布订单
```
POST /api/v1/customer/orders/publish
Headers: Authorization: Bearer <token>
```

**请求体**:
```json
{
  "title": "需要维修电脑",
  "description": "笔记本电脑无法开机",
  "service_type": "it_technology",
  "price": 200.00,
  "location": "NORTH",
  "address": "北京市朝阳区XX小区",
  "service_start_time": "2025-10-25T09:00:00",
  "service_end_time": "2025-10-25T12:00:00"
}
```

**验证规则**:
- title: 非空
- price: > 0
- service_type: 有效枚举值
- service_end_time > service_start_time
- 只有role_id=1可以发布

**响应** (200):
```json
{
  "order_id": 1,
  "message": "订单发布成功，等待管理员审核"
}
```

**业务逻辑**:
1. 验证用户为客户
2. 验证字段有效性
3. 创建订单 (status=pending_review, payment_status=unpaid)
4. 插入customer_inbox通知: "您的订单已发布，等待管理员审核"
5. 返回order_id

---

### 3.2 获取客户进行中订单
```
GET /api/v1/customer/orders/my
Headers: Authorization: Bearer <token>
```

**响应** (200):
```json
[
  {
    "id": 1,
    "customer_id": 1,
    "provider_id": 2,
    "title": "需要维修电脑",
    "description": "笔记本电脑无法开机",
    "service_type": "it_technology",
    "status": "accepted",
    "price": 200.00,
    "location": "NORTH",
    "address": "北京市朝阳区XX小区",
    "service_start_time": "2025-10-25T09:00:00",
    "service_end_time": "2025-10-25T12:00:00",
    "payment_status": "unpaid",
    "created_at": "2025-10-24T10:00:00",
    "updated_at": "2025-10-24T11:00:00"
  }
]
```

**业务逻辑**:
1. 查询customer_id=当前用户 且 status NOT IN ('completed', 'cancelled')
2. 返回订单列表 (OrderDetail格式，15个字段)

---

### 3.3 获取客户订单详情
```
GET /api/v1/customer/orders/my/{order_id}
Headers: Authorization: Bearer <token>
```

**响应** (200): OrderDetail对象 (同上)

**业务逻辑**:
1. 验证订单归属 (customer_id=当前用户)
2. 返回订单详情

---

### 3.4 获取客户历史订单
```
GET /api/v1/customer/orders/history
Headers: Authorization: Bearer <token>
```

**响应** (200): OrderDetail数组

**业务逻辑**:
1. 查询customer_id=当前用户 且 status IN ('completed', 'cancelled')
2. 返回历史订单列表

---

### 3.5 客户取消订单
```
POST /api/v1/customer/orders/cancel/{order_id}
Headers: Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "message": "订单已取消"
}
```

**业务逻辑**:
1. 验证订单归属
2. 验证订单状态为pending或pending_review
3. 更新status=cancelled
4. 插入customer_inbox通知: "订单已取消"

**错误响应**:
- 400: 订单状态不允许取消

---

### 3.6 获取可接单列表
```
GET /api/v1/provider/orders/available
Headers: Authorization: Bearer <token>
```

**响应** (200): OrderDetail数组

**业务逻辑**:
1. 查询status='pending' (已审核通过的订单)
2. 返回订单列表

---

### 3.7 服务商接单
```
POST /api/v1/provider/orders/accept/{order_id}
Headers: Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "message": "成功接单"
}
```

**业务逻辑**:
1. 验证用户为服务商
2. 验证订单status='pending'
3. 验证provider_id为NULL (未被接单)
4. 更新provider_id=当前用户, status='accepted'
5. 插入customer_inbox: "您的订单已被服务商接受"
6. 插入provider_inbox: "您成功接受了订单"

**错误响应**:
- 400: 订单已被接单
- 400: 订单状态不正确

---

### 3.8 获取服务商订单详情
```
GET /api/v1/provider/orders/my/{order_id}
Headers: Authorization: Bearer <token>
```

**响应** (200): OrderDetail对象

**业务逻辑**:
1. 验证provider_id=当前用户
2. 返回订单详情

---

### 3.9 更新订单状态
```
POST /api/v1/provider/orders/status/{order_id}
Headers: Authorization: Bearer <token>
```

**请求体**:
```json
{
  "status": "in_progress"
}
```

**允许的状态流转**:
- accepted → in_progress
- in_progress → completed

**响应** (200):
```json
{
  "message": "订单状态已更新"
}
```

**业务逻辑**:
1. 验证provider_id=当前用户
2. 验证状态流转合法性
3. 更新订单状态
4. 插入customer_inbox和provider_inbox通知

---

### 3.10 获取服务商历史订单
```
GET /api/v1/provider/orders/history
Headers: Authorization: Bearer <token>
```

**响应** (200): OrderDetail数组

**业务逻辑**:
1. 查询provider_id=当前用户 且 status IN ('completed', 'cancelled')
2. 返回历史订单

---

### 3.11 管理员获取所有订单
```
GET /api/v1/admin/orders?status=pending_review
Headers: Authorization: Bearer <token>
```

**查询参数**:
- status (可选): 过滤订单状态

**响应** (200): OrderDetail数组

**业务逻辑**:
1. 验证role_id=3
2. 查询所有订单 (可按status过滤)
3. 返回订单列表

---

### 3.12 获取待审核订单
```
GET /api/v1/admin/orders/pending-review
Headers: Authorization: Bearer <token>
```

**响应** (200): OrderDetail数组

**业务逻辑**:
1. 验证role_id=3
2. 查询status='pending_review'的订单
3. 返回订单列表

---

### 3.13 审批订单
```
POST /api/v1/admin/orders/{order_id}/approve
Headers: Authorization: Bearer <token>
```

**请求体**:
```json
{
  "approved": true,
  "reject_reason": "订单信息不完整"
}
```

**字段说明**:
- approved: true=批准, false=拒绝
- reject_reason: 拒绝时必填

**响应** (200):
```json
{
  "message": "订单已批准"
}
```

**业务逻辑**:

**批准订单** (approved=true):
1. 验证role_id=3
2. 验证订单status='pending_review'
3. 更新status='pending'
4. 插入customer_inbox: "Your order #{order_id} has been approved by admin and is now available for providers to accept."

**拒绝订单** (approved=false):
1. 验证role_id=3
2. 验证订单status='pending_review'
3. 验证reject_reason非空
4. 更新status='cancelled'
5. 插入customer_inbox: "Your order #{order_id} has been rejected. Reason: {reject_reason}"

---

### 3.14 管理员更新订单
```
PUT /api/v1/admin/orders/{order_id}
Headers: Authorization: Bearer <token>
```

**请求体** (部分更新):
```json
{
  "title": "更新后的标题",
  "price": 250.00,
  "service_type": "cleaning_repair"
}
```

**响应** (200): 更新后的OrderDetail

**业务逻辑**:
1. 验证role_id=3
2. 更新订单字段
3. 返回更新后的订单

---

### 3.15 管理员删除订单
```
DELETE /api/v1/admin/orders/{order_id}
Headers: Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "message": "订单已删除"
}
```

**业务逻辑**:
1. 验证role_id=3
2. 物理删除订单记录

---

## 4. 支付服务 API

### 4.1 支付订单
```
POST /api/v1/customer/payments/pay
Headers: Authorization: Bearer <token>
```

**请求体**:
```json
{
  "order_id": 1
}
```

**响应** (200):
```json
{
  "message": "支付成功",
  "transaction_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**业务逻辑**:
1. 验证用户为客户
2. 验证订单存在且customer_id=当前用户
3. 验证订单status='completed'
4. 验证订单未支付 (payment_status='unpaid')
5. 生成transaction_id (UUID)
6. 创建支付记录 (payment_method='simulated', status='completed')
7. 更新订单payment_status='paid'
8. 插入customer_inbox: "订单 #{order_id} 支付成功"
9. 插入provider_inbox: "订单 #{order_id} 已收到付款"
10. 返回transaction_id

**错误响应**:
- 400: 订单未完成
- 400: 订单已支付

---

## 5. 评价服务 API

### 5.1 创建评价
```
POST /api/v1/reviews/create
Headers: Authorization: Bearer <token>
```

**请求体**:
```json
{
  "order_id": 1,
  "stars": 5,
  "content": "服务非常专业，态度很好"
}
```

**验证规则**:
- stars: 1-5
- order_id: 订单必须存在
- 订单必须已支付 (payment_status='paid')
- 订单未被评价过

**响应** (200):
```json
{
  "review_id": "507f1f77bcf86cd799439011",
  "message": "评价创建成功"
}
```

**业务逻辑**:
1. 验证用户为客户
2. 查询订单，验证customer_id=当前用户
3. 验证订单payment_status='paid'
4. 验证订单未被评价 (查询reviews集合)
5. 插入reviews集合
6. 查询该provider的所有评价
7. 计算平均评分和总数
8. 更新provider_profiles的rating和total_reviews
9. 插入provider_inbox: "客户对订单 #{order_id} 进行了评价（{stars}星）"
10. 返回review_id

**错误响应**:
- 400: 订单未支付
- 400: 订单已评价

---

### 5.2 获取服务商评价列表
```
GET /api/v1/reviews/provider/{provider_id}
Headers: Authorization: Bearer <token>
```

**响应** (200):
```json
[
  {
    "order_id": 1,
    "customer_id": 5,
    "provider_id": 2,
    "stars": 5,
    "content": "服务非常专业",
    "created_at": "2025-10-24T10:00:00Z"
  }
]
```

**业务逻辑**:
1. 查询reviews集合，provider_id=指定ID
2. 返回评价列表

---

## 6. 通知服务 API

### 6.1 获取客户通知
```
GET /api/v1/customer/inbox
Headers: Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "items": [
    {
      "customer_id": 1,
      "order_id": 123,
      "message": "您的订单已被接受",
      "is_read": false,
      "created_at": "2025-10-24T10:00:00Z"
    }
  ],
  "total": 5
}
```

**业务逻辑**:
1. 验证用户为客户
2. 查询customer_inbox，customer_id=当前用户
3. 按created_at降序排序
4. 返回通知列表和总数

---

### 6.2 获取服务商通知
```
GET /api/v1/provider/inbox
Headers: Authorization: Bearer <token>
```

**响应** (200): 同客户通知格式

**业务逻辑**:
1. 验证用户为服务商
2. 查询provider_inbox，provider_id=当前用户
3. 返回通知列表

---

## 📋 业务流程

### 完整订单流程

```
1. Customer注册 (role_id=1)
   └─> 创建customer_profile

2. Provider注册 (role_id=2)
   └─> 创建provider_profile

3. Customer发布订单
   POST /customer/orders/publish
   └─> 订单状态: pending_review
   └─> 通知Customer: "订单已发布，等待管理员审核"

4. Admin审核订单
   POST /admin/orders/{order_id}/approve
   ├─> approved=true
   │   └─> 订单状态: pending_review → pending
   │   └─> 通知Customer: "订单已批准"
   └─> approved=false
       └─> 订单状态: pending_review → cancelled
       └─> 通知Customer: "订单被拒绝: {reason}"

5. Provider查看可接单列表
   GET /provider/orders/available
   └─> 显示所有status='pending'的订单

6. Provider接单
   POST /provider/orders/accept/{order_id}
   └─> 订单状态: pending → accepted
   └─> 设置provider_id
   └─> 通知Customer: "订单已被接受"
   └─> 通知Provider: "成功接单"

7. Provider更新状态 (可选)
   POST /provider/orders/status/{order_id}
   └─> 订单状态: accepted → in_progress
   └─> 通知双方

8. Provider完成服务
   POST /provider/orders/status/{order_id}
   └─> 订单状态: in_progress → completed
   └─> 通知Customer: "订单已完成"

9. Customer支付
   POST /customer/payments/pay
   └─> payment_status: unpaid → paid
   └─> 创建支付记录
   └─> 通知Customer: "支付成功"
   └─> 通知Provider: "已收到付款"

10. Customer评价
    POST /reviews/create
    └─> 创建评价记录
    └─> 更新Provider评分
    └─> 通知Provider: "收到评价"
```

---

## 🔐 安全和认证

### JWT实现细节

**生成Token** (Python示例):
```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(user_id: int, role_id: int):
    payload = {
        "sub": str(user_id),
        "role": role_id,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

**验证Token**:
```python
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        role_id = payload.get("role")
        return user_id, role_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token已过期")
    except jwt.JWTError:
        raise HTTPException(401, "Token无效")
```

### 密码加密

**使用bcrypt**:
```python
import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )
```

### 权限控制

**中间件逻辑**:
```python
def require_role(allowed_roles: List[int]):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            token = get_token_from_header()
            user_id, role_id = verify_token(token)
            
            if role_id not in allowed_roles:
                raise HTTPException(403, "权限不足")
            
            # 将user_id注入到函数参数
            kwargs['current_user_id'] = user_id
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# 使用示例
@require_role([1])  # 只允许Customer
async def publish_order(current_user_id: int, ...):
    pass
```

---

## 🔄 事件驱动逻辑 (转为同步调用)

微服务架构中使用RabbitMQ发布事件，单体架构可以改为**直接函数调用**或**应用内事件总线**。

### 事件映射表

| 微服务事件 | 单体架构处理方式 | 触发时机 |
|-----------|----------------|---------|
| order.published | `notification_service.send_customer_notification()` | 订单发布后 |
| order.approved | `notification_service.send_customer_notification()` | 管理员批准后 |
| order.rejected | `notification_service.send_customer_notification()` | 管理员拒绝后 |
| order.accepted | `notification_service.send_customer_notification()`<br>`notification_service.send_provider_notification()` | Provider接单后 |
| order.status_updated | `notification_service.send_customer_notification()`<br>`notification_service.send_provider_notification()` | 订单状态更新后 |
| payment.completed | `notification_service.send_customer_notification()`<br>`notification_service.send_provider_notification()` | 支付成功后 |
| review.created | `notification_service.send_provider_notification()`<br>`user_service.update_provider_rating()` | 创建评价后 |

### 实现示例 (单体架构)

```python
# 订单服务中接单逻辑
async def accept_order(order_id: int, provider_id: int):
    # 1. 更新订单
    order = await order_dao.update_order(
        order_id, 
        provider_id=provider_id, 
        status='accepted'
    )
    
    # 2. 直接调用通知服务 (替代事件发布)
    await notification_service.send_customer_notification(
        customer_id=order.customer_id,
        order_id=order_id,
        message=f"您的订单 #{order_id} 已被服务商接受"
    )
    
    await notification_service.send_provider_notification(
        provider_id=provider_id,
        order_id=order_id,
        message=f"您成功接受了订单 #{order_id}"
    )
    
    return order
```

---

## 🎯 单体架构实现建议

### 推荐技术栈

**Backend**:
- **框架**: Django + Django REST Framework 或 FastAPI
- **ORM**: Django ORM 或 SQLAlchemy
- **认证**: django-rest-framework-simplejwt 或 python-jose
- **密码**: bcrypt
- **MySQL驱动**: aiomysql (异步) 或 pymysql (同步)
- **MongoDB驱动**: motor (异步) 或 pymongo (同步)

**数据库**:
- MySQL 8.0
- MongoDB 6.0
- Redis 7.0 (可选，用于缓存)

### 项目结构建议

```
monolith_app/
├── models/
│   ├── mysql/
│   │   ├── user.py          # User, Role
│   │   ├── order.py         # Order
│   │   └── payment.py       # Payment
│   └── mongodb/
│       ├── profile.py       # CustomerProfile, ProviderProfile
│       ├── review.py        # Review
│       └── notification.py  # CustomerInbox, ProviderInbox
├── services/
│   ├── auth_service.py      # 注册、登录、JWT
│   ├── user_service.py      # 资料管理
│   ├── order_service.py     # 订单管理
│   ├── payment_service.py   # 支付逻辑
│   ├── review_service.py    # 评价逻辑
│   └── notification_service.py  # 通知逻辑
├── api/
│   ├── auth_api.py
│   ├── user_api.py
│   ├── order_api.py
│   ├── payment_api.py
│   ├── review_api.py
│   └── notification_api.py
├── middleware/
│   └── auth.py              # JWT验证、权限控制
├── database/
│   ├── mysql_connection.py
│   └── mongodb_connection.py
└── main.py
```

### 数据库连接配置

```python
# MySQL连接 (SQLAlchemy)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

MYSQL_URL = "mysql+pymysql://user:password@localhost:3306/freelancer"
engine = create_engine(MYSQL_URL)
SessionLocal = sessionmaker(bind=engine)

# MongoDB连接
from pymongo import MongoClient

MONGODB_URL = "mongodb://localhost:27017"
mongo_client = MongoClient(MONGODB_URL)
mongo_db = mongo_client["freelancer"]
```

### 关键实现要点

1. **合并数据库**: 
   - 微服务中3个MySQL数据库 → 1个MySQL数据库
   - 微服务中3个MongoDB数据库 → 1个MongoDB数据库

2. **移除服务间通信**:
   - 微服务中HTTP调用 → 直接函数调用
   - 例如: `order_service.get_order()` 替代 `http://order-service:8003/api/...`

3. **事件处理**:
   - RabbitMQ事件 → 同步函数调用
   - 或使用Django Signals等应用内事件

4. **保持API一致性**:
   - 保持所有API路由和响应格式不变
   - 方便前端无缝迁移

5. **事务管理**:
   - 跨服务操作变为本地事务
   - 例如: 支付成功 → 更新订单状态可以在同一事务中完成

---

## 📊 数据迁移清单

### MySQL表迁移

| 微服务 | 原数据库 | 表名 | 迁移到 |
|-------|---------|-----|-------|
| Auth Service | auth_db | users | freelancer_db.users |
| Auth Service | auth_db | roles | freelancer_db.roles |
| Order Service | order_db | orders | freelancer_db.orders |
| Payment Service | payment_db | payments | freelancer_db.payments |

### MongoDB集合迁移

| 微服务 | 原数据库 | 集合名 | 迁移到 |
|-------|---------|-------|-------|
| User Service | user_db | customer_profiles | freelancer_db.customer_profiles |
| User Service | user_db | provider_profiles | freelancer_db.provider_profiles |
| Review Service | review_db | reviews | freelancer_db.reviews |
| Notification Service | notification_db | customer_inbox | freelancer_db.customer_inbox |
| Notification Service | notification_db | provider_inbox | freelancer_db.provider_inbox |

---

## ✅ 功能检查清单

实现完成后，请验证以下功能:

### 用户认证
- [ ] 用户注册 (3种角色)
- [ ] 用户登录 (生成JWT)
- [ ] JWT验证和解析
- [ ] 密码bcrypt加密

### 用户资料
- [ ] 客户资料 CRUD
- [ ] 服务商资料 CRUD
- [ ] 角色权限验证

### 订单管理
- [ ] 客户发布订单 (status=pending_review)
- [ ] 管理员审核订单 (批准/拒绝)
- [ ] 服务商查看可接单列表 (status=pending)
- [ ] 服务商接单
- [ ] 订单状态流转 (in_progress, completed)
- [ ] 订单查询 (进行中/历史)
- [ ] 管理员管理订单

### 支付系统
- [ ] 模拟支付 (status=completed订单)
- [ ] 生成交易ID (UUID)
- [ ] 更新订单支付状态

### 评价系统
- [ ] 创建评价 (paid订单)
- [ ] 自动更新Provider评分
- [ ] 查询Provider评价列表

### 通知系统
- [ ] 订单发布通知
- [ ] 订单审核通知 (批准/拒绝)
- [ ] 订单接受通知
- [ ] 订单状态更新通知
- [ ] 支付成功通知
- [ ] 评价通知
- [ ] 通知查询接口

---

## 📝 API测试示例

### Postman测试流程

1. **注册Customer**:
```
POST /api/v1/auth/register
{
  "username": "customer1",
  "email": "customer@example.com",
  "password": "Pass123",
  "role_id": 1
}
```

2. **注册Provider**:
```
POST /api/v1/auth/register
{
  "username": "provider1",
  "email": "provider@example.com",
  "password": "Pass123",
  "role_id": 2
}
```

3. **注册Admin**:
```
POST /api/v1/auth/register
{
  "username": "admin1",
  "email": "admin@example.com",
  "password": "Pass123",
  "role_id": 3
}
```

4. **Customer登录获取Token**:
```
POST /api/v1/auth/login
{
  "email": "customer@example.com",
  "password": "Pass123"
}
→ 保存 customer_token
```

5. **Customer创建资料**:
```
POST /api/v1/customer/profile
Headers: Authorization: Bearer {customer_token}
{
  "location": "NORTH",
  "budget_preference": 1000
}
```

6. **Customer发布订单**:
```
POST /api/v1/customer/orders/publish
Headers: Authorization: Bearer {customer_token}
{
  "title": "电脑维修",
  "service_type": "it_technology",
  "price": 200,
  "location": "NORTH",
  "service_start_time": "2025-10-25T09:00:00",
  "service_end_time": "2025-10-25T12:00:00"
}
→ 获得 order_id = 1
```

7. **Admin登录并审核**:
```
POST /api/v1/auth/login
{
  "email": "admin@example.com",
  "password": "Pass123"
}
→ 保存 admin_token

POST /api/v1/admin/orders/1/approve
Headers: Authorization: Bearer {admin_token}
{
  "approved": true
}
```

8. **Provider登录并接单**:
```
POST /api/v1/auth/login
{
  "email": "provider@example.com",
  "password": "Pass123"
}
→ 保存 provider_token

POST /api/v1/provider/orders/accept/1
Headers: Authorization: Bearer {provider_token}
```

9. **Provider完成订单**:
```
POST /api/v1/provider/orders/status/1
Headers: Authorization: Bearer {provider_token}
{
  "status": "in_progress"
}

POST /api/v1/provider/orders/status/1
Headers: Authorization: Bearer {provider_token}
{
  "status": "completed"
}
```

10. **Customer支付**:
```
POST /api/v1/customer/payments/pay
Headers: Authorization: Bearer {customer_token}
{
  "order_id": 1
}
```

11. **Customer评价**:
```
POST /api/v1/reviews/create
Headers: Authorization: Bearer {customer_token}
{
  "order_id": 1,
  "stars": 5,
  "content": "Very good service!"
}
```

12. **查看通知**:
```
GET /api/v1/customer/inbox
Headers: Authorization: Bearer {customer_token}

GET /api/v1/provider/inbox
Headers: Authorization: Bearer {provider_token}
```

---

## 🔍 常见问题

### Q1: MongoDB字段_id如何处理？
A: MongoDB自动生成_id字段，但我们的模型不使用它。在查询时使用`doc.pop("_id", None)`移除，使用user_id或order_id作为业务主键。

### Q2: 订单状态为什么不包括paid？
A: paid不是订单状态，而是payment_status。订单状态最终为completed，支付状态为paid。

### Q3: 如何实现事务一致性？
A: 单体架构中，MySQL操作可以使用数据库事务。MongoDB操作需要注意幂等性，必要时可以使用MongoDB事务（4.0+支持）。

### Q4: 如何处理并发接单？
A: 使用数据库乐观锁或悲观锁。例如:
```sql
UPDATE orders 
SET provider_id = ?, status = 'accepted'
WHERE id = ? AND status = 'pending' AND provider_id IS NULL
```
检查affected_rows是否为1。

### Q5: 时区如何处理？
A: 建议统一使用UTC时间存储，前端展示时转换为本地时区。Python使用`datetime.utcnow()`。

---

## 📚 附录

### A. service_type 枚举对照表

| 枚举值 | 中文名称 | 说明 |
|-------|---------|-----|
| cleaning_repair | 清洁与维修 | 家政、维修服务 |
| it_technology | IT与技术 | 软件开发、技术支持 |
| education_training | 教育与培训 | 教育、培训、辅导 |
| life_health | 生活与健康 | 健身、咨询、护理 |
| design_consulting | 设计与咨询 | 设计、咨询、策划 |
| other | 其他服务 | 未分类服务 |

### B. location 枚举对照表

| 枚举值 | 说明 |
|-------|-----|
| NORTH | 北部区域 |
| SOUTH | 南部区域 |
| EAST | 东部区域 |
| WEST | 西部区域 |
| MID | 中部区域 |

### C. 所有订单状态

| 状态 | 说明 | 可转换到 |
|-----|-----|---------|
| pending_review | 待审核 | pending, cancelled |
| pending | 待接单 | accepted, cancelled |
| accepted | 已接单 | in_progress, cancelled |
| in_progress | 进行中 | completed, cancelled |
| completed | 已完成 | - (终态) |
| cancelled | 已取消 | - (终态) |

### D. HTTP状态码规范

| 状态码 | 使用场景 |
|-------|---------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或Token无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 📞 总结

本文档提供了将微服务架构转换为单体架构所需的全部技术细节：

✅ **完整的数据库表结构** (MySQL 4张表 + MongoDB 5个集合)  
✅ **所有API接口规格** (33个API端点)  
✅ **详细的业务逻辑** (字段验证、状态流转、权限控制)  
✅ **认证和安全机制** (JWT、bcrypt、角色权限)  
✅ **完整的业务流程** (订单从发布到评价的全流程)  
✅ **实现建议和示例代码**  

使用本文档，您可以：
1. 理解系统的完整业务逻辑
2. 创建数据库表和集合
3. 实现所有API接口
4. 编写业务逻辑代码
5. 测试功能完整性

**关键转换要点**:
- 合并所有数据库到一个MySQL + 一个MongoDB
- 移除RabbitMQ，改为直接函数调用
- 保持API接口不变，方便前端对接
- 简化部署和运维

祝您开发顺利！

---

**文档版本**: v1.0  
**创建日期**: 2025-10-24  
**适用于**: 微服务 → 单体架构迁移

