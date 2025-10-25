from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, validator
from app.config import get_db
from app.services.customer_service import publish_order, cancel_order, get_my_orders, get_order_detail, get_order_history, review_order
from app.models.models import LocationEnum, OrderStatus, ServiceType
from typing import Optional, List
from jose import JWTError, jwt
from app.dependencies import get_current_user  # 导入依赖 # Import dependency

class PublishOrderRequest(BaseModel):
    title: str
    description: Optional[str] = None
    service_type: ServiceType
    price: float
    location: LocationEnum
    address: Optional[str] = None
    service_start_time: Optional[str] = None
    service_end_time: Optional[str] = None

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

class OrderSummary(BaseModel):
    id: int
    title: str
    service_type: str
    status: str
    price: float
    location: str
    created_at: str

class OrderDetail(BaseModel):
    id: int
    customer_id: int
    provider_id: Optional[int]
    title: str
    description: Optional[str]
    service_type: str
    status: str
    price: float
    location: str
    address: Optional[str]
    service_start_time: Optional[str]
    service_end_time: Optional[str]
    payment_status: str
    created_at: str
    updated_at: str
    review: Optional[dict] = None

class ReviewOrderRequest(BaseModel):
    order_id: int
    stars: int = 5
    content: Optional[str] = None

    @validator("stars")
    def stars_valid(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Stars must be between 1 and 5")
        return v

class ReviewOrderResponse(BaseModel):
    review_id: int
    order_id: int
    stars: int
    content: Optional[str]
    message: str

orders_router = APIRouter(prefix='/api/v1/customer/orders', tags=['orders'])

@orders_router.post("/publish", response_model=PublishOrderResponse)
async def publish_order_route(
    data: PublishOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)  # 实际项目应启用此行 # Enable this line in production
    # current_user_id: int = Depends(lambda: 3)  # 演示用，实际应从token获取 # For demo, should get from token

    # 如果你准备启用token解析，取消上面注释，注释掉lambda: 3
    # If you want to enable token parsing, uncomment above and comment out lambda: 3

):
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
        # Prompt when order cannot be cancelled
        raise HTTPException(status_code=400, detail=str(e))
    return CancelOrderResponse(
        order_id=order.id,
        status=order.status.value,
        message=f"You have successfully cancelled the order: {order.id}."
    )

@orders_router.get("/my", response_model=List[OrderSummary])
async def list_my_orders(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    orders = await get_my_orders(db, current_user_id)
    return [
        OrderSummary(
            id=o.id,
            title=o.title,
            service_type=o.service_type.value,
            status=o.status.value,
            price=float(o.price),
            location=o.location.value,
            created_at=str(o.created_at)
        )
        for o in orders
    ]

@orders_router.get("/my/{order_id}", response_model=OrderDetail)
async def get_my_order_detail(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    order = await get_order_detail(db, current_user_id, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order  # 直接返回 dict，Pydantic 会自动转换

@orders_router.get("/history", response_model=List[OrderSummary])
async def list_order_history(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    orders = await get_order_history(db, current_user_id)
    return [
        OrderSummary(
            id=o.id,
            title=o.title,
            service_type=o.service_type.value,
            status=o.status.value,
            price=float(o.price),
            location=o.location.value,
            created_at=str(o.created_at)
        )
        for o in orders
    ]

@orders_router.post("/review", response_model=ReviewOrderResponse)
async def review_order_route(
    data: ReviewOrderRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    客户评价订单接口
    Customer reviews order API
    """
    try:
        review = await review_order(db, current_user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ReviewOrderResponse(
        review_id=review.id,
        order_id=review.order_id,
        stars=review.stars,
        content=review.content,
        message=f"Review submitted for order {review.order_id}."
    )