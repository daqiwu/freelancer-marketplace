from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_db
from app.dependencies import get_current_user
from app.models.models import LocationEnum, OrderStatus
from app.services.provider_service import (
    list_available_orders,
    accept_order,
    update_order_status,
    list_provider_order_history,
    get_order_detail_for_provider,
)


class OrderItem(BaseModel):
    id: int
    title: str
    price: float
    location: LocationEnum
    address: Optional[str] = None
    # status is implicitly pending for this endpoint; include for completeness
    status: str

    class Config:
        from_attributes = True


class BrowseOrdersResponse(BaseModel):
    items: List[OrderItem]
    total: int


provider_orders_router = APIRouter(prefix="/api/v1/provider/orders", tags=["provider-orders"])


@provider_orders_router.get("/available", response_model=BrowseOrdersResponse)
async def browse_available_orders(
    *,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
    location: Optional[LocationEnum] = Query(default=None),
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    keyword: Optional[str] = Query(default=None, description="Search in title/description"),
):
    orders = await list_available_orders(
        db,
        location=location,
        min_price=min_price,
        max_price=max_price,
        keyword=keyword,
    )
    items = [
        OrderItem(
            id=o.id,
            title=o.title,
            price=float(o.price) if o.price is not None else 0.0,
            location=o.location,
            address=o.address,
            status=o.status.value,
        )
        for o in orders
    ]
    return BrowseOrdersResponse(items=items, total=len(items))


# -------- Accept Order --------
class AcceptOrderResponse(BaseModel):
    order_id: int
    status: str
    message: str


@provider_orders_router.post("/accept/{order_id}", response_model=AcceptOrderResponse)
async def accept_order_route(
    order_id: int,
    *,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    try:
        order = await accept_order(db, provider_id=current_user_id, order_id=order_id)
    except ValueError as e:
        # When order is already accepted or invalid, return failure notification
        raise HTTPException(status_code=400, detail=str(e))

    # Success notice (also to be displayed on web for 1~2 secs)
    return AcceptOrderResponse(
        order_id=order.id,
        status=order.status.value,
        message=f"You have successfully accepted the order: {order.id}.",
    )


# -------- Update Order Status --------
class UpdateStatusRequest(BaseModel):
    new_status: OrderStatus  # expecting in_progress or completed


class UpdateStatusResponse(BaseModel):
    order_id: int
    status: str
    message: str


@provider_orders_router.post("/status/{order_id}", response_model=UpdateStatusResponse)
async def update_status_route(
    order_id: int,
    data: UpdateStatusRequest,
    *,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    try:
        order = await update_order_status(
            db,
            provider_id=current_user_id,
            order_id=order_id,
            new_status=data.new_status,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return UpdateStatusResponse(
        order_id=order.id,
        status=order.status.value,
        message=f"Order {order.id} status updated to {order.status.value}.",
    )


# -------- Provider Order History --------
class HistoryItem(BaseModel):
    id: int
    title: str
    price: float
    location: LocationEnum
    address: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    items: List[HistoryItem]
    total: int


@provider_orders_router.get("/history", response_model=HistoryResponse)
async def provider_history_route(
    *,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    orders = await list_provider_order_history(db, provider_id=current_user_id)
    items = [
        HistoryItem(
            id=o.id,
            title=o.title,
            price=float(o.price) if o.price is not None else 0.0,
            location=o.location,
            address=o.address,
            status=o.status.value,
        )
        for o in orders
    ]
    return HistoryResponse(items=items, total=len(items))


# -------- Provider Order Detail --------
class ProviderOrderDetail(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    price: float
    location: str
    address: Optional[str]
    created_at: str
    updated_at: str
    provider_id: Optional[int]
    review: Optional[dict] = None


@provider_orders_router.get("/my/{order_id}", response_model=ProviderOrderDetail)
async def get_my_order_detail_for_provider(
    order_id: int,
    *,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    order = await get_order_detail_for_provider(db, provider_id=current_user_id, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

