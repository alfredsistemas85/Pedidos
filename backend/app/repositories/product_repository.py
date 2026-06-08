from app.core.supabase import supabase
from app.domain.models import Producto
from app.core.exceptions import RepositoryException
from typing import List

class ProductRepository:
    @staticmethod
    def get_all() -> List[Producto]:
        try:
            res = supabase.table("productos").select("*").eq("activo", True).execute()
            return [Producto(**p) for p in res.data]
        except Exception as e:
            raise RepositoryException(f"Error al obtener productos: {str(e)}")
            
    @staticmethod
    def get_by_id(product_id: str) -> Producto:
        try:
            res = supabase.table("productos").select("*").eq("id", product_id).execute()
            if not res.data:
                return None
            return Producto(**res.data[0])
        except Exception as e:
            raise RepositoryException(f"Error al obtener producto {product_id}: {str(e)}")

    @staticmethod
    def create(producto: Producto) -> Producto:
        try:
            data = producto.model_dump(exclude_unset=True, exclude={"id"})
            res = supabase.table("productos").insert(data).execute()
            return Producto(**res.data[0])
        except Exception as e:
            raise RepositoryException(f"Error al crear producto: {str(e)}")

    @staticmethod
    def update(product_id: str, datos: dict) -> Producto:
        try:
            res = supabase.table("productos").update(datos).eq("id", product_id).execute()
            if not res.data:
                return None
            return Producto(**res.data[0])
        except Exception as e:
            raise RepositoryException(f"Error al actualizar producto {product_id}: {str(e)}")

    @staticmethod
    def soft_delete(product_id: str) -> Producto:
        try:
            res = supabase.table("productos").update({"activo": False}).eq("id", product_id).execute()
            if not res.data:
                return None
            return Producto(**res.data[0])
        except Exception as e:
            raise RepositoryException(f"Error al eliminar producto {product_id}: {str(e)}")
