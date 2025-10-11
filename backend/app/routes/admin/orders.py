from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_db
from app.dependencies import get_current_user
from typing import List, Optional
from pydantic import BaseModel
from app.models.models import LocationEnum, OrderStatus
from app.services.admin_service import list_all_orders

class AdminOrderItem(BaseModel):
	id: int
	title: str
	price: float
	location: LocationEnum
	address: Optional[str] = None
	status: str
	customer_id: int
	provider_id: Optional[int] = None
	created_at: str
	updated_at: str

	class Config:
		from_attributes = True

class AdminOrdersResponse(BaseModel):
	items: List[AdminOrderItem]
	total: int

admin_orders_router = APIRouter(prefix="/admin/orders", tags=["admin-orders"])

@admin_orders_router.get("/all", response_model=AdminOrdersResponse)
async def list_all_orders_route(
	db: AsyncSession = Depends(get_db),
	current_user_id: int = Depends(get_current_user),
	status: Optional[str] = Query(default=None, description="Order status filter"),
):
	orders = await list_all_orders(db, status=status)
	items = [
		AdminOrderItem(
			id=o.id,
			title=o.title,
			price=float(o.price) if o.price is not None else 0.0,
			location=o.location,
			address=o.address,
			status=o.status.value,
			customer_id=o.customer_id,
			provider_id=getattr(o, "provider_id", None),
			created_at=str(o.created_at),
			updated_at=str(o.updated_at),
		)
		for o in orders
	]
	return AdminOrdersResponse(items=items, total=len(items))

