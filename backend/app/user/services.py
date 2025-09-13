from app.user.models import UserCreate, User, UserLogin
from app.database.session import DBsession

from sqlmodel import select
from fastapi import HTTPException

async def user_register(user: UserCreate, dbsession: DBsession) -> int:
    user_email_check = await dbsession.exec(select(User).where(User.email == user.email)).first()
    if user_email_check:
        raise HTTPException(status_code=400, detail="User already exists")

    user_name_check = await dbsession.exec(select(User).where(User.name == user.name)).first()
    if user_name_check:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(name=user.name, email=user.email, password=user.password)
    dbsession.add(user)
    await dbsession.commit()
    await dbsession.refresh(user)

    return user.id

async def user_login(user: UserLogin, dbsession: DBsession) -> int:
    user_check = await dbsession.exec(select(User).where(User.email == user.email)).first()
    if not user_check:
        raise HTTPException(status_code=400, detail="User not found")

    if user_check.password != user.password:
        raise HTTPException(status_code=400, detail="Invalid password")

    return user_check.id