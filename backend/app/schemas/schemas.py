from pydantic import BaseModel, EmailStr


# 用于用户注册的请求体模型
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


# 用于用户注册的响应体模型
class UserCreateResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True  # 允许从 ORM 对象（SQLAlchemy 模型）转换


# 用于用户登录的请求体模型
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# 用于用户登录的响应体模型
class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str
