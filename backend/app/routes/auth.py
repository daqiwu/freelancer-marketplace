from fastapi import APIRouter

from app.schemas.schemas import UserCreateResponse, UserCreate, UserLoginResponse, UserLogin
from app.database.session import DBsession
from app.services.auth_service import user_register, user_login

user_router = APIRouter(prefix='/user')

@user_router.post("/register", response_model=UserCreateResponse)
async def register(user: UserCreate, dbsession: DBsession):
    user = await user_register(user, dbsession)
    return UserCreateResponse(id=user)

@user_router.post("/login", response_model=UserLoginResponse)
async def login(user: UserLogin, dbsession: DBsession):
    user = await user_login(user, dbsession)
    return UserLoginResponse(id=user)