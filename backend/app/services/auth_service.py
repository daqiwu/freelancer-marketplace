<<<<<<< HEAD
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import User
import bcrypt
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "your_secret_key"  # 建议放到环境变量
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

async def register_user(db: AsyncSession, username: str, email: str, password: str, role_id: int):
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User(
        username=username,
        email=email,
        password_hash=hashed_pw,
        role_id=role_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user and user.verify_password(password):
        return user
    return None

async def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
=======
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
>>>>>>> dev
