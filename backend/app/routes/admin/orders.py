from fastapi import APIRouter, Depends, HTTPException, Query, status
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

admin_orders_router = APIRouter(prefix="/admin", tags=["admin-orders"])



@admin_orders_router.get("/orders", response_model=AdminOrdersResponse, responses={
	401: {"description": "Unauthorized", "content": {"application/json": {"example": {"error": "Authentication required."}}}},
	422: {"description": "Validation Error", "content": {"application/json": {"example": {"error": "Validation failed.", "details": {}}}}},
	500: {"description": "Internal Server Error", "content": {"application/json": {"example": {"error": "Internal server error."}}}},
})
async def list_all_orders_route(
	db: AsyncSession = Depends(get_db),
	current_user_id: int = Depends(get_current_user),
	status: Optional[str] = Query(default=None, description="Order status filter"),
	page: int = Query(default=1, ge=1, description="Page number"),
	limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
	sort_by: Optional[str] = Query(default="created_at", description="Sort by field"),
	order: Optional[str] = Query(default="desc", description="Sort order: asc or desc"),
):
	try:
		orders = await list_all_orders(
			db,
			status=status,
			page=page,
			limit=limit,
			sort_by=sort_by,
			order=order
		)
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
	except HTTPException as e:
		# Pass through FastAPI HTTPExceptions (e.g. 401)
		return {"error": e.detail}
	except ValueError as ve:
		# Validation error
		raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"error": "Validation failed.", "details": str(ve)})
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "Error Fetching orders", "details": str(e)})

