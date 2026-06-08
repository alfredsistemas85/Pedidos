import inspect
from functools import wraps
from fastapi import Request, HTTPException, status
import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 días

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)
    return encoded_jwt

from app.core.logger import logger

def decode_access_token(token: str) -> dict:
    try:
        decoded_data = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        return decoded_data
    except Exception as e:
        logger.error(f"Fallo al decodificar JWT local: {type(e).__name__} - {str(e)}")
        return None

def require_role(allowed_roles: list[str]):
    """
    Decorador estricto para validar el rol de request.state.role.
    Soporta funciones sync y async.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get("request")
            if not request and len(args) > 0:
                request = args[0]
                
            if not request:
                raise HTTPException(status_code=500, detail="Missing Request object in endpoint for @require_role validation")

            role = getattr(request.state, "role", None)
            
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated. JWT token missing or invalid."
                )

            if role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Forbidden: insufficient permissions"
                )
                
            if inspect.iscoroutinefunction(func):
                return await func(*args, **kwargs)

            return func(*args, **kwargs)
            
        return wrapper
    return decorator
