from app.models.models import User
from app.schemas.schemas import UserCreate, UserLogin
from app.database.session import DBsession

from sqlmodel import select
from fastapi import HTTPException
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def user_register(user: UserCreate, dbsession: DBsession) -> int:
    # 1. 检查邮箱是否存在
    result_email = await dbsession.exec(select(User).where(User.email == user.email))
    user_email_check = result_email.first()

    if user_email_check:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # 2. 检查用户名是否存在
    result_name = await dbsession.exec(select(User).where(User.username == user.username))
    user_name_check = result_name.first()

    if user_name_check:
        raise HTTPException(status_code=400, detail="User with this username already exists")
    
    hashed_password = get_password_hash(user.password)

    # 3. 创建新用户
    new_user = User(username=user.username, email=user.email, password_hash=hashed_password, role_id=1)
    dbsession.add(new_user)
    await dbsession.commit()
    await dbsession.refresh(new_user)

    return new_user

async def user_login(user: UserLogin, dbsession: DBsession) -> int:
    result = await dbsession.exec(select(User).where(User.email == user.email))
    user_check = result.first()
    
    if not user_check or not verify_password(user.password, user_check.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return user_check