from fastapi import APIRouter

from app.routes.auth import auth_router

marketplace_router = APIRouter(prefix='/freelancer/marketplace')

marketplace_router.include_router(auth_router)