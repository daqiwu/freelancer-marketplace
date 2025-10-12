from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from app.config import get_db
from app.dependencies import get_current_user
from app.models.models import User, Role
from app.services.admin_service import list_users_by_role, delete_user_by_id, get_user_by_id

class UserItem(BaseModel):
	id: int
	username: str
	email: str
	role_id: int
	created_at: str
	updated_at: str

	class Config:
		from_attributes = True

class UsersResponse(BaseModel):
	items: List[UserItem]
	total: int


admin_users_router = APIRouter(prefix="/admin/users", tags=["admin-users"])



@admin_users_router.get("/", response_model=UsersResponse)
async def list_users_route(
	role_id: Optional[int] = Query(default=None, description="1=customer, 2=provider"),
	page: int = Query(default=1, ge=1, description="Page number"),
	limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
	sort_by: Optional[str] = Query(default="created_at", description="Sort by field"),
	order: Optional[str] = Query(default="desc", description="Sort order: asc or desc"),
	db: AsyncSession = Depends(get_db),
	current_user_id: int = Depends(get_current_user),
):
	try:
		users = await list_users_by_role(
			db,
			role_id,
			page=page,
			limit=limit,
			sort_by=sort_by,
			order=order
		)
		items = [
			UserItem(
				id=u.id,
				username=u.username,
				email=u.email,
				role_id=u.role_id,
				created_at=str(u.created_at),
				updated_at=str(u.updated_at),
			)
			for u in users
		]
		return UsersResponse(items=items, total=len(items))
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

# New route to view a specific user
from fastapi import HTTPException

@admin_users_router.get("/{id}", response_model=UserItem)
async def get_user_route(
	id: int,
	db: AsyncSession = Depends(get_db),
	current_user_id: int = Depends(get_current_user),
):
	try:
		user = await get_user_by_id(db, id)
		if not user:
			raise HTTPException(status_code=404, detail="User not found")
		return UserItem(
			id=user.id,
			username=user.username,
			email=user.email,
			role_id=user.role_id,
			created_at=str(user.created_at),
			updated_at=str(user.updated_at),
		)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")


@admin_users_router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_user_route(
	id: int,
	db: AsyncSession = Depends(get_db),
	current_user_id: int = Depends(get_current_user),
):
	try:
		await delete_user_by_id(db, id)
		return {"detail": f"User {id} deleted successfully."}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")
