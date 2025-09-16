# app/user/services.py (修改后)

from app.user.models import UserCreate, User, UserLogin
from app.database.session import DBsession

from sqlmodel import select
from fastapi import HTTPException

async def user_register(user: UserCreate, dbsession: DBsession) -> int:
    # 1. 检查邮箱是否存在
    result_email = await dbsession.exec(select(User).where(User.email == user.email))
    user_email_check = result_email.first()
    # --- 修改结束 ---
    if user_email_check:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # 2. 检查用户名是否存在
    result_name = await dbsession.exec(select(User).where(User.name == user.name))
    user_name_check = result_name.first()

    if user_name_check:
        raise HTTPException(status_code=400, detail="User with this name already exists")
    
    # 3. 创建新用户
    new_user = User(name=user.name, email=user.email, password=user.password)
    dbsession.add(new_user)
    await dbsession.commit()
    await dbsession.refresh(new_user)

    return new_user.id

async def user_login(user: UserLogin, dbsession: DBsession) -> int:
    # 1. 查找用户
    result = await dbsession.exec(select(User).where(User.email == user.email))
    user_check = result.first()
    
    if not user_check:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. 验证密码
    if user_check.password != user.password:
        raise HTTPException(status_code=400, detail="Invalid password")

    return user_check.id