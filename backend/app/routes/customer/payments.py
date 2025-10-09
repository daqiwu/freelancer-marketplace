from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.config import get_db
from app.dependencies import get_current_user
from app.models.models import CustomerProfile, Order, PaymentStatus, OrderStatus # 导入所需模型 # Import necessary models
from pydantic import BaseModel
import decimal

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
    balance: float
    message: str

@payments_router.post("/pay", response_model=PayOrderResponse)
async def pay_order(
    data: PayOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    客户支付订单接口
    Customer pay order API
    """
    # 查询订单  # Query order
    result = await db.execute(
        select(Order).where(Order.id == data.order_id, Order.customer_id == current_user_id)
    )
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在  // Order not found")
    if order.status != OrderStatus.completed:
        raise HTTPException(status_code=400, detail="订单未完成，无法支付  // Order not completed, cannot pay")
    if order.payment_status == PaymentStatus.paid:
        raise HTTPException(status_code=400, detail="订单已支付  // Order already paid")
    # 查询客户余额  # Query customer balance
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == current_user_id)
    )
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="未找到客户资料  // Customer profile not found")
    if profile.balance < order.price:
        raise HTTPException(status_code=400, detail="余额不足，请充值  // Insufficient balance, please recharge")
    # 扣款并更新订单支付状态  # Deduct and update order payment status
    profile.balance -= order.price
    order.payment_status = PaymentStatus.paid
    await db.commit()
    await db.refresh(profile)
    await db.refresh(order)
    return PayOrderResponse(
        order_id=order.id,
        balance=float(profile.balance),
        message=f"支付成功，订单 {order.id} 已支付  // Payment successful, order {order.id} is paid"
    )