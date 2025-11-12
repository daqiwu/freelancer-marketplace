import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    @property
    def DATABASE_URL(self) -> str:
        # Use DATABASE_URL environment variable (managed database)
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return database_url.strip()

        # Fallback: construct from individual components
        db_user = os.getenv("DB_USER", "freelancer")
        db_password = os.getenv("DB_PASSWORD", "password123")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME", "freelancer_marketplace")

        return f"mysql+aiomysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


settings = Settings()

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
