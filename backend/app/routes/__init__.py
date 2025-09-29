<<<<<<< HEAD
from fastapi import APIRouter

<<<<<<<< HEAD:backend/app/routes/__init__.py
from app.routes.auth import auth_router
========
from app.routes.auth import user_router
>>>>>>>> dev:backend/app/router.py

marketplace_router = APIRouter(prefix='/freelancer/marketplace')

marketplace_router.include_router(auth_router)
=======
# Routes package
>>>>>>> dev
