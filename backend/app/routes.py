from fastapi import APIRouter

from app.user.routes import user_router

marketplace_router = APIRouter(prefix='/freelancer/marketplace')

marketplace_router.include_router(user_router)