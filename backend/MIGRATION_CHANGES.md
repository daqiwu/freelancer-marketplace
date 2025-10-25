# 后端代码调整总结

根据《微服务转单体架构 - 完整技术文档》，已对后端代码进行以下调整：

## 1. 数据模型更新 (models.py)

### 新增枚举类型
- **ServiceType**: 服务类型枚举
  - cleaning_repair (清洁与维修)
  - it_technology (IT与技术)
  - education_training (教育与培训)
  - life_health (生活与健康)
  - design_consulting (设计与咨询)
  - other (其他服务)

- **PaymentMethodEnum**: 支付方式枚举
  - simulated (模拟支付)

- **PaymentStatusEnum**: 支付记录状态枚举
  - pending (待处理)
  - completed (已完成)
  - failed (失败)

### 更新 OrderStatus 枚举
- **新增**: `pending_review` (待审核) - 作为订单的默认初始状态
- **移除**: `reviewed` (已评价) - 评价不再作为订单状态

订单状态流转：
```
pending_review → pending → accepted → in_progress → completed
                                                       ↓
                                                   cancelled
```

### Order 模型更新
新增字段：
- `service_type`: 服务类型（必填）
- `service_start_time`: 服务开始时间
- `service_end_time`: 服务结束时间
- 默认状态改为 `pending_review`

### 新增 Payment 模型
创建独立的支付记录表：
- `order_id`: 订单ID（唯一）
- `customer_id`: 客户ID
- `provider_id`: 服务商ID
- `amount`: 支付金额
- `payment_method`: 支付方式（固定为 simulated）
- `status`: 支付状态
- `transaction_id`: 交易ID（UUID，唯一）

### Review 模型更新
- `order_id` 添加唯一约束，确保每个订单只能被评价一次

## 2. API 路由更新

所有路由添加 `/api/v1` 前缀，符合文档规范：

- `/api/v1/auth/*` - 认证相关
- `/api/v1/customer/orders/*` - 客户订单
- `/api/v1/customer/payments/*` - 客户支付
- `/api/v1/provider/orders/*` - 服务商订单
- `/api/v1/provider/earnings/*` - 服务商收入
- `/api/v1/admin/orders/*` - 管理员订单管理
- `/api/v1/admin/users/*` - 管理员用户管理
- `/api/v1/profile/*` - 用户资料
- `/api/v1/notification/*` - 通知

## 3. 认证服务更新 (auth_service.py)

### JWT Token 结构更新
新增 `create_access_token_with_role` 函数，Token payload 包含：
```json
{
  "sub": "user_id",
  "role": role_id,
  "exp": timestamp
}
```

### 新增接口
- `GET /api/v1/auth/me`: 获取当前用户信息

## 4. 订单服务更新

### 客户订单服务 (customer_service.py)

#### publish_order (发布订单)
- 默认状态改为 `pending_review`
- 支持 `service_type`, `service_start_time`, `service_end_time`
- 通知消息：提示等待管理员审核

#### cancel_order (取消订单)
- 允许取消状态：`pending_review` 和 `pending`（原来是 `pending` 和 `accepted`）

#### get_my_orders (获取进行中订单)
- 包含 `pending_review` 状态的订单

#### review_order (评价订单)
- 移除订单状态更新为 `reviewed` 的逻辑
- 只要求订单 `payment_status` 为 `paid`

### 管理员订单服务 (admin_service.py)

#### 新增功能

1. **get_pending_review_orders**
   - 获取所有待审核订单
   - 路由: `GET /api/v1/admin/orders/pending-review`

2. **approve_order**
   - 管理员审批订单
   - 路由: `POST /api/v1/admin/orders/{order_id}/approve`
   - 参数:
     - `approved`: true/false
     - `reject_reason`: 拒绝原因（拒绝时必填）
   - 批准后状态: `pending_review` → `pending`
   - 拒绝后状态: `pending_review` → `cancelled`
   - 发送通知给客户

3. **update_order**
   - 管理员更新订单
   - 路由: `PUT /api/v1/admin/orders/{order_id}`
   - 支持更新: title, price, service_type, description, location, address

4. **delete_order**
   - 管理员删除订单
   - 路由: `DELETE /api/v1/admin/orders/{order_id}`
   - 级联删除相关的通知和评价

## 5. Schemas 更新

### PublishOrderRequest
新增字段：
- `service_type`: ServiceType
- `service_start_time`: Optional[str]
- `service_end_time`: Optional[str]

### OrderDetail
更新字段列表（15个字段）：
- id, customer_id, provider_id
- title, description, service_type
- status, price, location, address
- service_start_time, service_end_time
- payment_status, created_at, updated_at
- review (可选)

### OrderSummary
新增字段：
- `service_type`: str

## 6. 支付服务更新 (payments.py)

### pay_order (支付订单)
更新为符合文档规范：
- 生成 UUID 作为 `transaction_id`
- 创建 `Payment` 记录（payment_method=simulated, status=completed）
- 更新订单 `payment_status` 为 `paid`
- 发送通知给客户和服务商
- 返回 `transaction_id`

响应格式更新：
```json
{
  "order_id": 1,
  "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "支付成功"
}
```

## 7. 数据库迁移

创建新的迁移文件: `add_service_fields_to_orders.py`

包含：
1. 添加 service_type, service_start_time, service_end_time 字段
2. 更新 status 枚举
3. 创建 payments 表
4. 为 reviews.order_id 添加唯一约束

## 8. 业务流程更新

### 完整订单流程
```
1. Customer 发布订单
   └─> status: pending_review
   └─> 通知客户: "订单已发布，等待管理员审核"

2. Admin 审核订单
   ├─> 批准: status → pending
   │   └─> 通知: "订单已批准，等待服务商接单"
   └─> 拒绝: status → cancelled
       └─> 通知: "订单已拒绝: {原因}"

3. Provider 接单
   └─> status: pending → accepted

4. Provider 完成服务
   └─> status: in_progress → completed

5. Customer 支付
   └─> payment_status: unpaid → paid
   └─> 创建 Payment 记录

6. Customer 评价
   └─> 创建 Review 记录
   └─> 通知 Provider
```

## 9. 关键变更说明

### 状态管理
- **订单创建**: 默认 `pending_review`，需要管理员审核
- **订单取消**: 只能在 `pending_review` 或 `pending` 状态下取消
- **订单评价**: 移除 `reviewed` 状态，评价不改变订单状态

### 数据完整性
- 每个订单最多一个支付记录（order_id 唯一）
- 每个订单最多一次评价（order_id 唯一）
- 服务类型成为必填字段

### API 规范
- 统一使用 `/api/v1` 前缀
- JWT Token 包含 role 信息
- 错误响应格式统一

## 10. 待办事项

- [ ] 运行数据库迁移脚本
- [ ] 更新前端 API 调用路径（添加 /api/v1 前缀）
- [ ] 测试完整的订单流程
- [ ] 测试管理员审批功能
- [ ] 验证 JWT Token 中的 role 字段

## 11. 注意事项

1. **数据库迁移**: 需要谨慎执行，建议先在开发环境测试
2. **现有数据**: 迁移脚本会将现有的 `pending` 状态改为 `pending_review`
3. **前端兼容性**: 需要更新前端代码以适应新的 API 路径和字段
4. **API 版本**: 使用 `/api/v1` 前缀便于未来版本升级

## 12. 测试建议

测试完整流程：
1. 注册 Customer, Provider, Admin 用户
2. Customer 发布订单（包含新字段）
3. Admin 审核订单（批准/拒绝）
4. Provider 接单
5. Provider 更新订单状态
6. Customer 支付订单
7. Customer 评价订单
8. 验证通知功能

