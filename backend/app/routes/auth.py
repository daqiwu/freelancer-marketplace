from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from sqlalchemy.future import select
# from app.models.models import User
from app.services.auth_service import register_user, authenticate_user, create_access_token, logout_user
from app.config import get_db
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

auth_router = APIRouter(prefix='/auth', tags=['auth'])

@auth_router.post("/register", response_model=RegisterResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await register_user(db, data.username, data.email, data.password, data.role_id)
    return RegisterResponse(id=user.id, username=user.username, email=user.email)

@auth_router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = await create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)


@auth_router.post("/logout")
async def logout():
    return await logout_user()
