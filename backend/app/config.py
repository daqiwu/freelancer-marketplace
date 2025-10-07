import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine
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
            return os.getenv("DOCKER_DATABASE_URL").strip()
        return os.getenv("LOCAL_DATABASE_URL").strip()

settings = Settings()

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
