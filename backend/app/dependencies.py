from fastapi import HTTPException, Request
from jose import JWTError, jwt

SECRET_KEY = "your_secret_key"  # Recommended to read from environment variable
ALGORITHM = "HS256"


def get_current_user(request: Request):
    """
    Parse JWT token from Authorization header to get current user ID
    In actual projects, improve exception handling and user validation
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
