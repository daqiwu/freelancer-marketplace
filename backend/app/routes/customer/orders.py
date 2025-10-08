from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, validator
from app.config import get_db
from app.services.customer_service import publish_order, cancel_order
from app.models.models import LocationEnum, OrderStatus
from typing import Optional
from jose import JWTError, jwt
from app.dependencies import get_current_user  # 导入依赖

class PublishOrderRequest(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    location: LocationEnum
    address: Optional[str] = None

    @validator("title")
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v

    @validator("price")
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v

class PublishOrderResponse(BaseModel):
    order_id: int
    status: str
    message: str

class CancelOrderResponse(BaseModel):
    order_id: int
    status: str
    message: str

orders_router = APIRouter(prefix='/customer/orders', tags=['orders'])

@orders_router.post("/publish", response_model=PublishOrderResponse)
async def publish_order_route(
    data: PublishOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)  # 实际项目应启用此行
    # current_user_id: int = Depends(lambda: 3)  # 演示用，实际应从token获取
):
    # 如果你准备启用token解析，取消上面注释，注释掉lambda: 3
    try:
        order = await publish_order(db, current_user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return PublishOrderResponse(
        order_id=order.id,
        status=order.status.value,
        message=f"You have successfully published the order: {order.id}."
    )

@orders_router.post("/cancel/{order_id}", response_model=CancelOrderResponse)
async def cancel_order_route(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    try:
        order = await cancel_order(db, current_user_id, order_id)
    except ValueError as e:
        # 订单不可取消时的提示
        raise HTTPException(status_code=400, detail=str(e))
    return CancelOrderResponse(
        order_id=order.id,
        status=order.status.value,
        message=f"You have successfully cancelled the order: {order.id}."
    )