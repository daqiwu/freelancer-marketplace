import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    USE_DOCKER: bool = os.getenv("USE_DOCKER", "false").lower() == "true"

    @property
    def DATABASE_URL(self) -> str:
        if self.USE_DOCKER:
            return os.getenv("DOCKER_DATABASE_URL").strip()
        return os.getenv("LOCAL_DATABASE_URL").strip()

settings = Settings()
