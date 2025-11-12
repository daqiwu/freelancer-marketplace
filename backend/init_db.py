# backend/init_db.py
import asyncio
from datetime import UTC, datetime

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.models import Base, Role, User

DATABASE_URL = settings.DATABASE_URL

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Async database initialization"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        try:
            # Create roles
            for role_name in ["customer", "provider", "admin"]:
                from sqlalchemy.future import select

                result = await session.execute(
                    select(Role).where(Role.role_name == role_name)
                )
                existing_role = result.scalar_one_or_none()

                if not existing_role:
                    new_role = Role(role_name=role_name)
                    session.add(new_role)

            await session.commit()

            # Create preset admin account
            result = await session.execute(
                select(Role).where(Role.role_name == "admin")
            )
            admin_role = result.scalar_one_or_none()

            if admin_role:
                # Check if admin account already exists
                result = await session.execute(
                    select(User).where(User.email == "admin@freelancer-platform.com")
                )
                existing_admin = result.scalar_one_or_none()

                if not existing_admin:
                    # Create admin account
                    admin_password = "AdminSecure2024!"  # Strong password
                    hashed_password = bcrypt.hashpw(
                        admin_password.encode("utf-8"), bcrypt.gensalt()
                    ).decode("utf-8")

                    admin_user = User(
                        username="system_admin",
                        email="admin@freelancer-platform.com",
                        password_hash=hashed_password,
                        role_id=admin_role.id,
                        created_at=datetime.now(UTC),
                        updated_at=datetime.now(UTC),
                    )
                    session.add(admin_user)
                    await session.commit()

                    print("✅ Preset admin account created successfully!")
                    print(f"   Username: system_admin")
                    print(f"   Email: admin@freelancer-platform.com")
                    print(f"   Password: AdminSecure2024!")
                    print(f"   Role: Admin")
                else:
                    print("ℹ️  Admin account already exists, skipping creation")
            else:
                print("❌ Admin role does not exist, cannot create admin account")

        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            await session.rollback()
            import traceback

            traceback.print_exc()

    print("Database initialization completed")


def run_init_db():
    """Sync wrapper"""
    asyncio.run(init_db())


if __name__ == "__main__":
    run_init_db()
