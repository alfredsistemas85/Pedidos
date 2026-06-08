from app.core.supabase import supabase
from app.domain.models import Cliente
from app.core.exceptions import RepositoryException
from typing import Optional

class ClientRepository:
    @staticmethod
    def get_by_phone(telefono: str) -> Optional[Cliente]:
        try:
            res = supabase.table("clientes").select("*").eq("telefono", telefono).execute()
            if res.data and len(res.data) > 0:
                return Cliente(**res.data[0])
            return None
        except Exception as e:
            raise RepositoryException(f"Error al obtener cliente por teléfono: {str(e)}")

    @staticmethod
    def create(cliente: Cliente) -> Cliente:
        try:
            data = cliente.model_dump(exclude_unset=True, exclude={"id"})
            res = supabase.table("clientes").insert(data).execute()
            return Cliente(**res.data[0])
        except Exception as e:
            raise RepositoryException(f"Error al crear cliente: {str(e)}")
            
    @staticmethod
    def update(cliente_id: str, updates: dict) -> Cliente:
        try:
            res = supabase.table("clientes").update(updates).eq("id", cliente_id).execute()
            return Cliente(**res.data[0])
        except Exception as e:
            raise RepositoryException(f"Error al actualizar cliente: {str(e)}")
