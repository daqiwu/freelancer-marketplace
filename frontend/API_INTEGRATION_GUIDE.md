# 前端API集成指南

## 概述

本项目已完成前后端API集成，实现了完整的自由职业者平台功能。

## 已实现的功能

### 1. 认证系统 ✅
- **注册功能** (`/register`)
  - 支持客户和服务提供者注册
  - 邮箱验证和密码强度检查
  - 自动创建用户资料

- **登录功能** (`/login`)
  - 邮箱+密码登录
  - JWT token认证
  - 自动获取用户信息

- **登出功能**
  - 清除本地token
  - 跳转到登录页面

### 2. 用户信息管理 ✅
- **获取用户信息** (`/profile/me`)
  - 根据角色返回不同信息
  - 客户：包含客户资料
  - 服务提供者：包含服务商资料

- **更新资料**
  - 客户资料更新
  - 服务商资料更新

### 3. 客户订单管理 ✅
- **发布订单** (`/customer/orders/publish`)
  - 订单标题、描述、价格
  - 地点选择（北区/南区/东区/西区/中区）
  - 详细地址

- **订单管理** (`/customer/orders`)
  - 查看所有订单
  - 订单状态筛选
  - 订单统计

- **订单操作**
  - 取消订单
  - 支付订单
  - 评价订单

### 4. 支付系统 ✅
- **余额管理**
  - 充值余额
  - 查看余额

- **订单支付**
  - 支付已完成订单
  - 余额扣除

### 5. 通知系统 ✅
- **消息收件箱**
  - 客户收件箱
  - 服务商收件箱
  - 消息分类筛选

- **消息操作**
  - 标记已读
  - 删除消息

## 技术实现

### API服务层 (`/src/services/api.js`)
```javascript
// 统一的API调用服务
class ApiService {
  // 认证相关
  async register(userData)
  async login(credentials)
  async logout()
  
  // 用户信息
  async getUserProfile()
  async updateCustomerProfile(profileData)
  async updateProviderProfile(profileData)
  
  // 订单管理
  async publishOrder(orderData)
  async getMyOrders()
  async getOrderHistory()
  async cancelOrder(orderId)
  async reviewOrder(reviewData)
  
  // 支付功能
  async rechargeBalance(amount)
  async payOrder(orderId)
  
  // 通知功能
  async getCustomerInbox()
  async getProviderInbox()
}
```

### 页面组件

#### 1. 认证页面
- **Login.vue** - 登录页面
- **Register.vue** - 注册页面

#### 2. 客户功能页面
- **CustomerOrders.vue** - 订单管理页面
- **Messages.vue** - 消息通知页面

#### 3. 测试页面
- **TestPage.vue** - API测试页面

### 路由配置
```javascript
// 新增路由
{
  path: '/customer/orders',
  name: 'CustomerOrders',
  component: () => import('@/views/CustomerOrders.vue')
},
{
  path: '/test',
  name: 'Test',
  component: () => import('@/views/TestPage.vue')
}
```

## 使用方法

### 1. 启动后端服务
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 启动前端服务
```bash
cd frontend
npm run serve
```

### 3. 访问页面
- **首页**: `http://localhost:8080/`
- **登录**: `http://localhost:8080/login`
- **注册**: `http://localhost:8080/register`
- **客户订单**: `http://localhost:8080/customer/orders`
- **消息通知**: `http://localhost:8080/messages`
- **API测试**: `http://localhost:8080/test`

## API测试

访问 `/test` 页面可以测试所有API接口：

1. **认证测试** - 注册、登录、登出
2. **用户信息测试** - 获取和更新用户资料
3. **订单测试** - 发布、查看、取消订单
4. **支付测试** - 充值、支付订单
5. **通知测试** - 获取收件箱消息

## 错误处理

- **网络错误** - 显示友好错误信息
- **API错误** - 根据错误码显示具体错误
- **降级处理** - API失败时显示示例数据

## 安全特性

- **JWT认证** - 所有API请求携带token
- **输入验证** - 前端表单验证
- **错误处理** - 统一的错误处理机制

## 下一步开发

1. **服务提供者功能** - 接单、管理任务
2. **订单详情页面** - 查看订单详细信息
3. **实时通知** - WebSocket推送
4. **文件上传** - 订单附件功能
5. **搜索功能** - 订单搜索和筛选

## 注意事项

1. **后端服务** - 确保后端API服务正常运行
2. **CORS配置** - 后端需要配置CORS允许前端访问
3. **数据库** - 确保数据库连接正常
4. **认证token** - 登录后token会保存在localStorage中

## 文件结构

```
frontend/src/
├── services/
│   └── api.js              # API服务层
├── views/
│   ├── Login.vue          # 登录页面
│   ├── Register.vue      # 注册页面
│   ├── CustomerOrders.vue # 客户订单页面
│   ├── Messages.vue      # 消息通知页面
│   └── TestPage.vue      # API测试页面
├── components/
│   └── NavBar.vue         # 导航栏组件
└── router/
    └── index.js          # 路由配置
```

现在前端已经完全集成了后端API，可以正常使用所有功能！
