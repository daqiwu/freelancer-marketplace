# backend/init_db.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, Role, User
from app.config import settings
import bcrypt
from datetime import datetime, UTC

DATABASE_URL = settings.DATABASE_URL

# 创建异步引擎
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    """异步初始化数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        try:
            # 创建角色
            for role_name in ["customer", "provider", "admin"]:
                from sqlalchemy.future import select
                result = await session.execute(select(Role).where(Role.role_name == role_name))
                existing_role = result.scalar_one_or_none()
                
                if not existing_role:
                    new_role = Role(role_name=role_name)
                    session.add(new_role)
            
            await session.commit()
            
            # 创建预设管理员账户
            result = await session.execute(select(Role).where(Role.role_name == "admin"))
            admin_role = result.scalar_one_or_none()
            
            if admin_role:
                # 检查是否已存在管理员账户
                result = await session.execute(select(User).where(User.email == "admin@freelancer-platform.com"))
                existing_admin = result.scalar_one_or_none()
                
                if not existing_admin:
                    # 创建管理员账户
                    admin_password = "AdminSecure2024!"  # 强密码
                    hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    
                    admin_user = User(
                        username="system_admin",
                        email="admin@freelancer-platform.com",
                        password_hash=hashed_password,
                        role_id=admin_role.id,
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC)
                    )
                    session.add(admin_user)
                    await session.commit()
                    
                    print("✅ 预设管理员账户创建成功！")
                    print(f"   用户名: system_admin")
                    print(f"   邮箱: admin@freelancer-platform.com")
                    print(f"   密码: AdminSecure2024!")
                    print(f"   角色: 管理员")
                else:
                    print("ℹ️  管理员账户已存在，跳过创建")
            else:
                print("❌ 管理员角色不存在，无法创建管理员账户")
                
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            await session.rollback()
            import traceback
            traceback.print_exc()
    
    print("数据库初始化完成")

def run_init_db():
    """同步包装器"""
    asyncio.run(init_db())

if __name__ == "__main__":
    run_init_db()