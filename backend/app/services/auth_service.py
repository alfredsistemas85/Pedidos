from app.core.supabase import supabase
from app.repositories.user_repository import UserRepository
from app.core.exceptions import UnauthorizedException
from typing import Dict

class AuthService:
    @staticmethod
    def login(email: str, password: str) -> Dict[str, str]:
        try:
            # Autenticación directa con Supabase Auth (GoTrue)
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            session = auth_response.session
            if not session:
                raise UnauthorizedException("Credenciales incorrectas")
                
            # Opcional: Obtener el rol del usuario de la tabla pública
            user_info = UserRepository.get_by_email(email)
            role = user_info.get("rol", "ADMIN") if user_info else "ADMIN"
            
            return {
                "access_token": session.access_token,
                "token_type": "bearer",
                "role": role
            }
        except Exception as e:
            # Si el error viene de Supabase Auth (como contraseñas incorrectas)
            raise UnauthorizedException(f"Credenciales incorrectas o error de inicio de sesión")
