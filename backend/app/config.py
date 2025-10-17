import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    @property
    def DATABASE_URL(self) -> str:
        aws_url = os.getenv("AWS_DATABASE_URL")
        if aws_url:
            return aws_url.strip()
        use_docker = os.getenv("USE_DOCKER", "false").lower() == "true"
        if use_docker:
            return os.getenv("DOCKER_DATABASE_URL", "mysql+aiomysql://root:password@db:3306/freelancer_marketplace").strip()
        return os.getenv("LOCAL_DATABASE_URL", "sqlite+aiosqlite:///./freelancer.db").strip()

settings = Settings()

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
