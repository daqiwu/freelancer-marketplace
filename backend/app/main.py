import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import engine
from app.models.models import Base
from app.routes import marketplace_router
from app.routes.admin.orders import admin_orders_router
from app.routes.admin.users import admin_users_router
from app.routes.auth import auth_router
from app.routes.customer.orders import orders_router
from app.routes.customer.payments import payments_router
from app.routes.notification import notification_router
from app.routes.profile import profile_router
from app.routes.provider.earnings import provider_earnings_router
from app.routes.provider.orders import provider_orders_router
from app.routes.review import review_router
from app.routes.security import security_router

app = FastAPI(
    title="FREELANCER MARKETPLACE", description="welcome to FREELANCER MARKETPLACE"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

app.include_router(marketplace_router)
app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(provider_orders_router)
app.include_router(provider_earnings_router)
app.include_router(payments_router)
app.include_router(profile_router)
app.include_router(admin_orders_router)
app.include_router(admin_users_router)
app.include_router(notification_router)
app.include_router(review_router)
app.include_router(security_router)


# 启动时创建数据库表
@app.on_event("startup")
async def startup_event():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("数据库表创建完成！")

        # 初始化数据库（包括创建管理员账户）
        from init_db import init_db

        await init_db()

    except Exception as e:
        print(f"数据库初始化失败: {e}")
        # 继续运行，不因为数据库问题停止服务


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
