from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_db
from app.dependencies import get_current_user
from typing import List, Optional
from pydantic import BaseModel
from app.models.models import LocationEnum, OrderStatus
from app.services.admin_service import list_all_orders, get_pending_review_orders, approve_order, update_order, delete_order

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

admin_orders_router = APIRouter(prefix="/api/v1/admin", tags=["admin-orders"])



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

@admin_orders_router.get("/orders/pending-review", response_model=AdminOrdersResponse)
async def get_pending_review_orders_route(
	db: AsyncSession = Depends(get_db),
	current_user_id: int = Depends(get_current_user)
):
	"""获取所有待审核订单"""
	try:
		orders = await get_pending_review_orders(db)
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
	except Exception as e:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "Error fetching pending review orders", "details": str(e)})

class ApproveOrderRequest(BaseModel):
	approved: bool
	reject_reason: Optional[str] = None

class ApproveOrderResponse(BaseModel):
	message: str

@admin_orders_router.post("/orders/{order_id}/approve", response_model=ApproveOrderResponse)
async def approve_order_route(
	order_id: int,
	data: ApproveOrderRequest,
	db: AsyncSession = Depends(get_db),
	current_user_id: int = Depends(get_current_user)
):
	"""管理员审批订单"""
	try:
		await approve_order(db, order_id, data.approved, data.reject_reason)
		if data.approved:
			return ApproveOrderResponse(message="订单已批准")
		else:
			return ApproveOrderResponse(message="订单已拒绝")
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=500, detail={"error": "Error approving order", "details": str(e)})

class UpdateOrderRequest(BaseModel):
	title: Optional[str] = None
	price: Optional[float] = None
	service_type: Optional[str] = None
	description: Optional[str] = None
	location: Optional[LocationEnum] = None
	address: Optional[str] = None

@admin_orders_router.put("/orders/{order_id}", response_model=AdminOrderItem)
async def update_order_route(
	order_id: int,
	data: UpdateOrderRequest,
	db: AsyncSession = Depends(get_db),
	current_user_id: int = Depends(get_current_user)
):
	"""管理员更新订单"""
	try:
		update_dict = data.dict(exclude_unset=True)
		order = await update_order(db, order_id, update_dict)
		return AdminOrderItem(
			id=order.id,
			title=order.title,
			price=float(order.price),
			location=order.location,
			address=order.address,
			status=order.status.value,
			customer_id=order.customer_id,
			provider_id=order.provider_id,
			created_at=str(order.created_at),
			updated_at=str(order.updated_at)
		)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))
	except Exception as e:
		raise HTTPException(status_code=500, detail={"error": "Error updating order", "details": str(e)})

class DeleteOrderResponse(BaseModel):
	message: str

@admin_orders_router.delete("/orders/{order_id}", response_model=DeleteOrderResponse)
async def delete_order_route(
	order_id: int,
	db: AsyncSession = Depends(get_db),
	current_user_id: int = Depends(get_current_user)
):
	"""管理员删除订单"""
	try:
		await delete_order(db, order_id)
		return DeleteOrderResponse(message="订单已删除")
	except Exception as e:
		raise HTTPException(status_code=500, detail={"error": "Error deleting order", "details": str(e)})

