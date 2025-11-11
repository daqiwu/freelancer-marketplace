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


# 🔒 Security Headers Middleware - DAST Protection
@app.middleware("http")
async def add_security_headers(request, call_next):
    """
    Add security headers to all responses to protect against common attacks.
    This fixes critical DAST findings:
    - HSTS: Prevents man-in-the-middle attacks
    - CSP: Prevents XSS and injection attacks
    - X-Frame-Options: Prevents clickjacking
    - X-Content-Type-Options: Prevents MIME sniffing
    """
    response = await call_next(request)
    
    # CRITICAL: Force HTTPS (prevents man-in-the-middle attacks)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # HIGH: Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # HIGH: Prevent clickjacking attacks
    response.headers["X-Frame-Options"] = "DENY"
    
    # HIGH: Content Security Policy (prevents XSS)
    # Allow unsafe-inline for Swagger UI to work properly
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
    )
    
    # MEDIUM: XSS Protection for legacy browsers
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # MEDIUM: Control referrer information leakage
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # LOW: Control browser features
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response


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


# 🏥 Root endpoint - AWS App Runner default health check
@app.get("/")
async def root():
    """
    Root endpoint for AWS App Runner default health check.
    Redirects to API documentation.
    """
    return {
        "message": "Freelancer Marketplace API",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# 🏥 Health check endpoint for AWS App Runner / Load Balancers
@app.get("/health")
async def health_check():
    """
    Health check endpoint for AWS App Runner, ALB, and monitoring.
    Returns 200 OK if the application is running.
    """
    return {
        "status": "healthy",
        "service": "freelancer-marketplace-api",
        "timestamp": "2025-11-07"
    }


# 启动时创建数据库表
@app.on_event("startup")
async def startup_event():
    """
    Initialize database on startup.
    Handles errors gracefully to prevent 502 errors in AWS App Runner.
    """
    try:
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ 数据库表创建完成！")

        # Initialize database (create admin account, etc.)
        # Import here to avoid circular dependencies
        try:
            from init_db import init_db
            await init_db()
            print("✅ 数据库初始化完成")
        except ImportError:
            print("⚠️  init_db module not found, skipping initialization")
        except Exception as init_error:
            print(f"⚠️  数据库初始化警告: {init_error}")
            # Continue anyway - admin account may already exist

    except Exception as e:
        print(f"❌ 数据库启动错误: {e}")
        # Don't raise - allow app to start even if DB connection fails temporarily
        # AWS App Runner needs the app to respond to health checks


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
