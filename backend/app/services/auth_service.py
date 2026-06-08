from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token
from app.core.exceptions import UnauthorizedException
from typing import Dict

class AuthService:
    @staticmethod
    def login(email: str, password: str) -> Dict[str, str]:
        user = UserRepository.get_by_email(email)
        if not user:
            raise UnauthorizedException("Credenciales incorrectas")
            
        password_hash = user.get("password_hash")
        
        # Rechazar inmediatamente si el usuario no tiene contraseña configurada
        if not password_hash:
            raise UnauthorizedException("Usuario sin credenciales configuradas. Contacte a soporte.")
            
        # Verificación criptográfica real
        if not verify_password(password, password_hash):
            raise UnauthorizedException("Credenciales incorrectas")

            
        token_data = {
            "sub": str(user["id"]),
            "role": user["rol"]
        }
        
        access_token = create_access_token(token_data)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user["rol"]
        }
