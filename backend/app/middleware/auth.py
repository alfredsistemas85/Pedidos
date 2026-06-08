from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import decode_access_token
from app.core.context import set_current_user, clear_current_user
from app.core.logger import logger

class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware que intercepta peticiones, valida JWT y carga 
    el contexto en Request State y en el ContextVar global.
    """
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        
        user_id = None
        role = None
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_access_token(token)
            if payload:
                user_id = payload.get("sub")
                role = payload.get("role")
            else:
                logger.warning("Token JWT inválido o expirado recibido.")
        
        # 1. Asignar a request.state para compatibilidad con dependencias FastAPI
        request.state.user_id = user_id
        request.state.role = role
        
        # 2. Asignar al Global ContextVar para uso profundo en Repositories/Services sin pasar 'request'
        set_current_user(user_id, role)
        
        try:
            response = await call_next(request)
            return response
        finally:
            clear_current_user() # Clean up memory to avoid cross-request contamination in async loop
