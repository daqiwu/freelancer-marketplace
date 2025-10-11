from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from app.config import get_db
from app.dependencies import get_current_user
from app.models.models import User, Role
from app.services.admin_service import list_users_by_role, delete_user_by_id

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

@admin_users_router.get("/list", response_model=UsersResponse)
async def list_users_route(
	role_id: Optional[int] = Query(default=None, description="1=customer, 2=provider"),
	db: AsyncSession = Depends(get_db),
	current_user_id: int = Depends(get_current_user),
):
	users = await list_users_by_role(db, role_id)
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

@admin_users_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(
	id: int,
	db: AsyncSession = Depends(get_db),
	current_user_id: int = Depends(get_current_user),
):
	await delete_user_by_id(db, id)
	return
