from fastapi import HTTPException, Request, Depends
from jose import JWTError, jwt

SECRET_KEY = "your_secret_key"  # 推荐从环境变量读取
ALGORITHM = "HS256"

def get_current_user(request: Request):
    """
    从 Authorization header 解析 JWT token，获取当前用户ID
    实际项目应完善异常处理和用户校验
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")