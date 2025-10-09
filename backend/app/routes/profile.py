from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user
from app.config import get_db
from sqlalchemy.future import select
from app.services.profile_service import (
    get_customer_profile,
    get_provider_profile,
    get_admin_profile,
    create_customer_profile,
    create_provider_profile
)
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

profile_router = APIRouter(prefix="/profile", tags=["profile"])

@profile_router.get("/me")
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    获取当前用户个人信息
    Get current user profile info
    """
    from app.models.models import User
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == current_user_id)
    )
    user = result.scalars().first()
    if not user or not user.role:
        raise HTTPException(status_code=404, detail="用户不存在  // User not found")
    role_name = user.role.role_name
    # 根据角色返回不同信息  # Return different info by role
    if role_name == "customer":
        profile = await get_customer_profile(db, current_user_id)
    elif role_name == "provider":
        profile = await get_provider_profile(db, current_user_id)
    elif role_name == "admin":
        profile = await get_admin_profile(db, current_user_id)
    else:
        raise HTTPException(status_code=400, detail="未知角色  // Unknown role")
    if not profile:
        raise HTTPException(status_code=404, detail="用户信息不存在  // User profile not found")
    return profile

class CreateCustomerProfileRequest(BaseModel):
    username: str
    location: str
    address: str
    budget_preference: float
    balance: float

@profile_router.post("/test/create_customer_profile")
async def test_create_customer_profile(
    data: CreateCustomerProfileRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    测试创建客户资料接口
    Test create customer profile API
    """
    # 查找用户ID  # Find user ID
    from app.models.models import User
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在  // User not found")
    profile = await create_customer_profile(
        db, user.id, data.location, data.address, data.budget_preference, data.balance
    )
    return {"msg": "客户资料创建成功  // Customer profile created", "profile_id": profile.id}

class CreateProviderProfileRequest(BaseModel):
    username: str
    skills: str
    experience_years: int
    hourly_rate: float
    availability: str

@profile_router.post("/test/create_provider_profile")
async def test_create_provider_profile(
    data: CreateProviderProfileRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    测试创建服务商资料接口
    Test create provider profile API
    """
    # 查找用户ID  # Find user ID
    from app.models.models import User
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在  // User not found")
    profile = await create_provider_profile(
        db, user.id, data.skills, data.experience_years, data.hourly_rate, data.availability
    )
    return {"msg": "服务商资料创建成功  // Provider profile created", "profile_id": profile.id}