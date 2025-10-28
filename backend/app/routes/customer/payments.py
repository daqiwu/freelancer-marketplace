from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config import get_db
from app.dependencies import get_current_user
from app.models.models import CustomerProfile, Order, PaymentStatus, OrderStatus, Payment, PaymentMethodEnum, PaymentStatusEnum # 导入所需模型 # Import necessary models
from pydantic import BaseModel
import decimal
import uuid
from datetime import datetime, UTC
from app.services.notification_service import send_customer_notification, send_provider_notification

payments_router = APIRouter(prefix='/customer/payments', tags=['payments'])

class RechargeRequest(BaseModel):
    amount: float

class RechargeResponse(BaseModel):
    balance: float
    message: str

@payments_router.post("/recharge", response_model=RechargeResponse)
async def recharge_balance(
    data: RechargeRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    客户充值余额接口
    Customer recharge balance API
    """
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="充值金额必须大于0  // Recharge amount must be greater than 0")
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == current_user_id)
    )
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="未找到客户资料  // Customer profile not found")
    profile.balance += decimal.Decimal(str(data.amount))  # 修正类型，避免类型错误
    await db.commit()
    await db.refresh(profile)
    return RechargeResponse(
        balance=float(profile.balance),
        message=f"充值成功，当前余额为 {profile.balance}  // Recharge successful, current balance is {profile.balance}"
    )

class PayOrderRequest(BaseModel):
    order_id: int

class PayOrderResponse(BaseModel):
    order_id: int
    transaction_id: str
    message: str

@payments_router.post("/pay", response_model=PayOrderResponse)
async def pay_order(
    data: PayOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    客户支付订单接口 (模拟支付)
    Customer pay order API (simulated payment)
    """
    # 查询订单  # Query order
    result = await db.execute(
        select(Order).where(Order.id == data.order_id, Order.customer_id == current_user_id)
    )
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    # 验证订单状态
    if order.status != OrderStatus.completed:
        raise HTTPException(status_code=400, detail="订单未完成，无法支付")
    if order.payment_status == PaymentStatus.paid:
        raise HTTPException(status_code=400, detail="订单已支付")
    
    # 生成交易ID
    transaction_id = str(uuid.uuid4())
    
    # 创建支付记录
    payment = Payment(
        order_id=order.id,
        customer_id=current_user_id,
        provider_id=order.provider_id,
        amount=order.price,
        payment_method=PaymentMethodEnum.simulated,
        status=PaymentStatusEnum.completed,
        transaction_id=transaction_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db.add(payment)
    
    # 更新订单支付状态
    order.payment_status = PaymentStatus.paid
    await db.commit()
    await db.refresh(payment)
    await db.refresh(order)
    
    # 发送通知
    await send_customer_notification(
        db, current_user_id, order.id,
        f"订单 #{order.id} 支付成功"
    )
    if order.provider_id:
        await send_provider_notification(
            db, order.provider_id, order.id,
            f"订单 #{order.id} 已收到付款"
        )
    
    return PayOrderResponse(
        order_id=order.id,
        transaction_id=transaction_id,
        message="支付成功"
    )