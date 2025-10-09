from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.models import User, CustomerProfile, ProviderProfile, Role

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
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.role_name if user.role else None,
        "created_at": str(user.created_at),
        "updated_at": str(user.updated_at),
        "customer_profile": {
            "id": user.customer_profile.id,
            "location": getattr(user.customer_profile.location, "value", user.customer_profile.location),
            "address": user.customer_profile.address,
            "budget_preference": float(user.customer_profile.budget_preference or 0),
            "balance": float(user.customer_profile.balance or 0),
            "created_at": str(user.customer_profile.created_at) if hasattr(user.customer_profile, "created_at") else None,
            "updated_at": str(user.customer_profile.updated_at) if hasattr(user.customer_profile, "updated_at") else None
        }
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
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.role_name if user.role else None,
        "created_at": str(user.created_at),
        "updated_at": str(user.updated_at),
        "provider_profile": {
            "id": user.provider_profile.id,
            "skills": user.provider_profile.skills,
            "experience_years": user.provider_profile.experience_years,
            "hourly_rate": float(user.provider_profile.hourly_rate or 0),
            "availability": user.provider_profile.availability,
            "created_at": str(user.provider_profile.created_at) if hasattr(user.provider_profile, "created_at") else None,
            "updated_at": str(user.provider_profile.updated_at) if hasattr(user.provider_profile, "updated_at") else None
        }
    }

async def get_admin_profile(db: AsyncSession, user_id: int):
    """
    获取管理员个人信息
    Get admin profile info
    """
    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == user_id)
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
        "updated_at": str(user.updated_at)
    }

async def create_customer_profile(db: AsyncSession, user_id: int, location: str, address: str, budget_preference: float, balance: float):
    """
    创建客户资料（测试专用）
    Create customer profile (for test only)
    """
    from app.models.models import CustomerProfile
    profile = CustomerProfile(
        id=user_id,
        location=location,
        address=address,
        budget_preference=budget_preference,
        balance=balance
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile

async def create_provider_profile(db: AsyncSession, user_id: int, skills: str, experience_years: int, hourly_rate: float, availability: str):
    """
    创建服务商资料（测试专用）
    Create provider profile (for test only)
    """
    from app.models.models import ProviderProfile
    profile = ProviderProfile(
        id=user_id,
        skills=skills,
        experience_years=experience_years,
        hourly_rate=hourly_rate,
        availability=availability
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile