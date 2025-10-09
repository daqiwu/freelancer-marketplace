from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import User, CustomerProfile, ProviderProfile, Role

async def get_user_profile(db: AsyncSession, user_id: int):
    """
    获取用户个人信息（支持客户、服务商、管理员）
    Get user profile info (support customer, provider, admin)
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        return None
    # 获取角色  # Get role
    role = user.role.role_name if user.role else None
    # 获取客户资料  # Get customer profile
    customer_profile = None
    if user.customer_profile:
        customer_profile = {
            "location": user.customer_profile.location.value,
            "address": user.customer_profile.address,
            "budget_preference": float(user.customer_profile.budget_preference or 0),
            "balance": float(user.customer_profile.balance or 0)
        }
    # 获取服务商资料  # Get provider profile
    provider_profile = None
    if user.provider_profile:
        provider_profile = {
            "skills": user.provider_profile.skills,
            "experience_years": user.provider_profile.experience_years,
            "hourly_rate": float(user.provider_profile.hourly_rate or 0),
            "availability": user.provider_profile.availability
        }
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": role,
        "created_at": str(user.created_at),
        "updated_at": str(user.updated_at),
        "customer_profile": customer_profile,
        "provider_profile": provider_profile
    }