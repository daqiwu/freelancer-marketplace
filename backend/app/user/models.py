from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=50, unique=True)
    email: str = Field(index=True, max_length=50, unique=True)
    password: str = Field()
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc),
        }
    )

class UserCreate(SQLModel):
    name: str = Field(max_length=50)
    email: str = Field(max_length=50)
    password: str = Field()

class UserCreateResponse(SQLModel):
    id: int

class UserLogin(SQLModel):
    email: str = Field(max_length=50)
    password: str = Field()

class UserLoginResponse(SQLModel):
    id: int