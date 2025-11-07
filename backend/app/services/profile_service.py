from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.models import CustomerProfile, ProviderProfile, Role, User


async def get_customer_profile(db: AsyncSession, user_id: int):
    """
    获取客户个人信息
    Get customer profile info
    """
    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.customer_profile))
        .where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user or not user.customer_profile:
        return None
    # 返回扁平化结构，方便前端直接使用
    return {
        "id": user.id,
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.role_name if user.role else None,
        "location": getattr(
            user.customer_profile.location, "value", user.customer_profile.location
        ),
        "address": user.customer_profile.address,
        "budget_preference": float(user.customer_profile.budget_preference or 0),
        "balance": float(user.customer_profile.balance or 0),
        "created_at": str(user.created_at),
        "updated_at": str(user.updated_at),
    }


async def get_provider_profile(db: AsyncSession, user_id: int):
    """
    获取服务商个人信息
    Get provider profile info
    """
    result = await db.execute(
        select(User)
        .options(selectinload(User.role), selectinload(User.provider_profile))
        .where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user or not user.provider_profile:
        return None
    # 返回扁平化结构，方便前端直接使用
    return {
        "id": user.id,
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.role_name if user.role else None,
        "skills": user.provider_profile.skills,
        "experience_years": user.provider_profile.experience_years,
        "hourly_rate": float(user.provider_profile.hourly_rate or 0),
        "availability": user.provider_profile.availability,
        "created_at": str(user.created_at),
        "updated_at": str(user.updated_at),
    }


async def get_admin_profile(db: AsyncSession, user_id: int):
    """
    获取管理员个人信息
    Get admin profile info
    """
    result = await db.execute(
        select(User).options(selectinload(User.role)).where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user or (user.role and user.role.role_name != "admin"):
        return None
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.role_name if user.role else None,
        "created_at": str(user.created_at),
        "updated_at": str(user.updated_at),
    }


async def update_customer_profile(
    db: AsyncSession,
    user_id: int,
    location: str,
    address: str,
    budget_preference: float,
    balance: float,
):
    """
    更新客户资料（首次更新即为创建，后续为更新）
    Update customer profile (create if not exists, else update)
    """
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.id == user_id)
    )
    profile = result.scalars().first()
    if not profile:
        # 首次创建
        profile = CustomerProfile(
            id=user_id,
            location=location,
            address=address,
            budget_preference=budget_preference,
            balance=balance,
        )
        db.add(profile)
    else:
        # 更新
        profile.location = location
        profile.address = address
        profile.budget_preference = budget_preference
        profile.balance = balance
    await db.commit()
    await db.refresh(profile)
    return profile


async def update_provider_profile(
    db: AsyncSession,
    user_id: int,
    skills: str,
    experience_years: int,
    hourly_rate: float,
    availability: str,
):
    """
    更新服务商资料（首次更新即为创建，后续为更新）
    Update provider profile (create if not exists, else update)
    """
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.id == user_id)
    )
    profile = result.scalars().first()
    if not profile:
        # 首次创建
        profile = ProviderProfile(
            id=user_id,
            skills=skills,
            experience_years=experience_years,
            hourly_rate=hourly_rate,
            availability=availability,
        )
        db.add(profile)
    else:
        # 更新
        profile.skills = skills
        profile.experience_years = experience_years
        profile.hourly_rate = hourly_rate
        profile.availability = availability
    await db.commit()
    await db.refresh(profile)
    return profile
