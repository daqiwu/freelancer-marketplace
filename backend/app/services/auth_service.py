from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import User, CustomerProfile, ProviderProfile, LocationEnum, Role
import bcrypt
from datetime import datetime, timedelta, UTC
from jose import jwt
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

SECRET_KEY = "your_secret_key"  # 建议放到环境变量 # Recommended to put in environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

async def register_user(db: AsyncSession, username: str, email: str, password: str, role_id: int):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User(
        username=username,
        email=email,
        password_hash=hashed_pw,
        role_id=role_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="用户名或邮箱已存在")  # Username or email already exists
    await db.refresh(user)

    # 查询角色名，避免懒加载
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    role_name = role.role_name if role else None

    if role_name == "customer":
        # 初始化客户资料
        profile = CustomerProfile(
            id=user.id,
            location=LocationEnum.NORTH,  # 默认值
            address=None,                 # 可为null
            budget_preference=0,          # 默认值
            balance=0                     # 默认值
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    elif role_name == "provider":
        # 初始化服务商资料
        profile = ProviderProfile(
            id=user.id,
            skills="",                    # 可为null或空字符串
            experience_years=0,           # 默认值
            hourly_rate=0,                # 默认值
            availability=None             # 可为null
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    # 管理员不需要 profile

    return user

async def authenticate_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user and user.verify_password(password):
        return user
    return None

async def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def logout_user():
    # JWT 无法在服务端失效，通常前端清除 token 即可
    # JWT cannot be invalidated on server side, usually frontend just clears the token
    return {"msg": "Logout successful"}
