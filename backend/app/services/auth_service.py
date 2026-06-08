from app.core.supabase import supabase
from app.repositories.user_repository import UserRepository
from app.core.exceptions import UnauthorizedException
from app.core.security import create_access_token
from typing import Dict

class AuthService:
    @staticmethod
    def login(email: str, password: str) -> Dict[str, str]:
        try:
            # 1. Autenticar contra Supabase Auth
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            session = auth_response.session
            if not session:
                raise UnauthorizedException("Credenciales incorrectas")
                
            # 2. Obtener la identidad del usuario (ID de Supabase)
            user_id = session.user.id
                
            # 3. Obtener el rol del usuario de nuestra tabla pública
            user_info = UserRepository.get_by_email(email)
            role = user_info.get("rol", "ADMIN") if user_info else "ADMIN"
            
            # 4. Generar nuestro propio JWT local (rápido, sin red, con rol inyectado)
            token_data = {
                "sub": user_id,
                "role": role
            }
            local_access_token = create_access_token(token_data)
            
            return {
                "access_token": local_access_token,
                "token_type": "bearer",
                "role": role
            }
        except Exception as e:
            raise UnauthorizedException(f"Credenciales incorrectas o error de inicio de sesión")
