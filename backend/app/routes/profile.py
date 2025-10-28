from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user
from app.config import get_db
from sqlalchemy.future import select
from app.services.profile_service import (
    get_customer_profile,
    get_provider_profile,
    get_admin_profile,
    update_customer_profile,
    update_provider_profile
)
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional

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

class UpdateCustomerProfileRequest(BaseModel):
    location: Optional[str] = None
    address: Optional[str] = None
    budget_preference: Optional[float] = None
    balance: Optional[float] = None

@profile_router.put("/update_customer_profile")
async def update_customer_profile_api(
    data: UpdateCustomerProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    更新客户资料接口
    Update customer profile API
    """
    # 只允许当前用户更新自己的 profile
    from app.models.models import User, CustomerProfile, LocationEnum
    result = await db.execute(select(User).where(User.id == current_user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在  // User not found")
    
    # 获取现有资料
    profile_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == current_user_id)
    )
    profile = profile_result.scalars().first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="客户资料不存在  // Customer profile not found")
    
    # 只更新提供的字段
    try:
        if data.location is not None:
            # 验证并转换 location
            if hasattr(LocationEnum, data.location):
                profile.location = LocationEnum[data.location]
            else:
                profile.location = data.location  # 如果是字符串直接赋值
        
        if data.address is not None:
            profile.address = data.address
        
        if data.budget_preference is not None:
            profile.budget_preference = data.budget_preference
        
        if data.balance is not None:
            profile.balance = data.balance
        
        # 标记对象已修改并提交
        db.add(profile)
        await db.flush()  # 先 flush 确保更改被检测
        await db.commit()
        await db.refresh(profile)
        
        return {"msg": "客户资料更新成功  // Customer profile updated", "profile_id": profile.id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")

class UpdateUserInfoRequest(BaseModel):
    username: str
    email: str

class UpdateProviderProfileRequest(BaseModel):
    skills: Optional[str] = None
    experience_years: Optional[int] = None
    hourly_rate: Optional[float] = None
    availability: Optional[str] = None

@profile_router.put("/update_provider_profile")
async def update_provider_profile_api(
    data: UpdateProviderProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    更新服务商资料接口
    Update provider profile API
    """
    # 只允许当前用户更新自己的 profile
    from app.models.models import User, ProviderProfile
    result = await db.execute(select(User).where(User.id == current_user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在  // User not found")
    
    # 获取现有资料
    profile_result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.id == current_user_id)
    )
    profile = profile_result.scalars().first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="服务商资料不存在  // Provider profile not found")
    
    # 只更新提供的字段
    try:
        if data.skills is not None:
            profile.skills = data.skills
        
        if data.experience_years is not None:
            profile.experience_years = data.experience_years
        
        if data.hourly_rate is not None:
            profile.hourly_rate = data.hourly_rate
        
        if data.availability is not None:
            profile.availability = data.availability
        
        # 标记对象已修改并提交
        db.add(profile)
        await db.flush()  # 先 flush 确保更改被检测
        await db.commit()
        await db.refresh(profile)
        
        return {"msg": "服务商资料更新成功  // Provider profile updated", "profile_id": profile.id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")

@profile_router.put("/update_user_info")
async def update_user_info_api(
    data: UpdateUserInfoRequest,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    """
    更新用户基本信息接口
    Update user basic info API
    """
    from app.models.models import User
    result = await db.execute(select(User).where(User.id == current_user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在  // User not found")
    
    # 更新用户基本信息
    user.username = data.username
    user.email = data.email
    await db.commit()
    await db.refresh(user)
    
    return {"msg": "用户信息更新成功  // User info updated", "user_id": user.id}