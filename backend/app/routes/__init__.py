from fastapi import APIRouter

from app.routes.auth import auth_router

marketplace_router = APIRouter(prefix='/api/v1')

# 不再需要重复包含 auth_router，因为它已经有自己的前缀
# marketplace_router.include_router(auth_router)

