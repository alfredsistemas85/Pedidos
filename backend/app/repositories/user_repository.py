from app.core.supabase import supabase
from app.domain.models import Usuario
from app.core.exceptions import RepositoryException, NotFoundException
from typing import Optional

class UserRepository:
    @staticmethod
    def get_by_email(email: str) -> Optional[dict]:
        try:
            res = supabase.table("usuarios").select("*").eq("email", email).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            return None
        except Exception as e:
            raise RepositoryException(f"Error al obtener usuario por email: {str(e)}")

    @staticmethod
    def get_by_id(user_id: str) -> Optional[dict]:
        try:
            res = supabase.table("usuarios").select("*").eq("id", user_id).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            return None
        except Exception as e:
            raise RepositoryException(f"Error al obtener usuario por id: {str(e)}")
