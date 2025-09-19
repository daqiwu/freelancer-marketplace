from typing import Annotated, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from fastapi import Depends, Request, HTTPException

from app.config import settings
from app.models.models import User

engine = create_async_engine(settings.DATABASE_URL, echo = True)

AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session()-> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

DBsession = Annotated[AsyncSession, Depends(get_session)]

async def get_current_user(request: Request, db: DBsession) -> User:
    user_id = getattr(request.state, "user_id", None) 
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found or token invalid")
        
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

# def db_init():
#     SQLModel.metadata.create_all(engine)