from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from sqlalchemy.future import select
from app.services.auth_service import register_user, authenticate_user, create_access_token, create_access_token_with_role, logout_user
from app.config import get_db
from app.dependencies import get_current_user
from pydantic import BaseModel
from app.models.models import User, Order

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role_id: int

class RegisterResponse(BaseModel):
    id: int
    username: str
    email: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserMeResponse(BaseModel):
    id: int
    username: str
    email: str
    role_id: int

auth_router = APIRouter(prefix='/api/v1/auth', tags=['auth'])

@auth_router.post("/register", response_model=RegisterResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, data.username, data.email, data.password, data.role_id)
    return RegisterResponse(id=user.id, username=user.username, email=user.email)

@auth_router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token_with_role(user.id, user.role_id)
    return TokenResponse(access_token=token)


@auth_router.get("/me", response_model=UserMeResponse)
async def get_me(db: AsyncSession = Depends(get_db), current_user_id: int = Depends(get_current_user)):
    """获取当前用户信息"""
    result = await db.execute(select(User).where(User.id == current_user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserMeResponse(id=user.id, username=user.username, email=user.email, role_id=user.role_id)

@auth_router.post("/logout")
async def logout():
    return await logout_user()
