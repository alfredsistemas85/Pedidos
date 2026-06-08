from app.core.supabase import supabase
from app.domain.models import Pedido, PedidoItem
from app.core.exceptions import RepositoryException
from typing import List, Optional

class OrderRepository:
    @staticmethod
    def create(pedido: Pedido, items: List[PedidoItem]) -> Pedido:
        try:
            # Transacción lógica (en Supabase REST API, hacemos múltiples llamadas)
            pedido_data = pedido.model_dump(exclude_unset=True, exclude={"id", "items"})
            
            # Insertar pedido
            res_pedido = supabase.table("pedidos").insert(pedido_data).execute()
            pedido_creado = res_pedido.data[0]
            
            # Insertar items
            items_data = []
            for item in items:
                item_data = item.model_dump(exclude_unset=True, exclude={"id"})
                item_data["pedido_id"] = pedido_creado["id"]
                items_data.append(item_data)
                
            if items_data:
                supabase.table("pedido_items").insert(items_data).execute()
                
            # Recuperar completo
            return OrderRepository.get_by_id(pedido_creado["id"])
        except Exception as e:
            raise RepositoryException(f"Error al crear pedido transaccional: {str(e)}")

    @staticmethod
    def get_by_id(pedido_id: str) -> Optional[Pedido]:
        try:
            res = supabase.table("pedidos").select("*, items:pedido_items(*)").eq("id", pedido_id).execute()
            if not res.data:
                return None
            data = res.data[0]
            return Pedido(**data)
        except Exception as e:
            raise RepositoryException(f"Error al obtener pedido: {str(e)}")
            
    @staticmethod
    def update_status(pedido_id: str, nuevo_estado: str) -> Pedido:
        try:
            res = supabase.table("pedidos").update({"estado": nuevo_estado}).eq("id", pedido_id).execute()
            return OrderRepository.get_by_id(res.data[0]["id"])
        except Exception as e:
            raise RepositoryException(f"Error al actualizar estado del pedido: {str(e)}")
            
    @staticmethod
    def get_all_active() -> List[Pedido]:
        try:
            res = supabase.table("pedidos").select("*, items:pedido_items(*)").neq("estado", "ENTREGADO").neq("estado", "CANCELADO").execute()
            return [Pedido(**p) for p in res.data]
        except Exception as e:
            raise RepositoryException(f"Error al listar pedidos activos: {str(e)}")

    @staticmethod
    def get_all_paginated(page: int, limit: int) -> dict:
        try:
            offset = (page - 1) * limit
            res = supabase.table("pedidos").select("*, items:pedido_items(*)", count="exact").order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            return {
                "data": [Pedido(**p) for p in res.data],
                "total": res.count,
                "page": page,
                "limit": limit
            }
        except Exception as e:
            raise RepositoryException(f"Error al listar pedidos paginados: {str(e)}")

    @staticmethod
    def obtener_ventas_hoy() -> float:
        try:
            from datetime import datetime, timezone
            today = datetime.now(timezone.utc).date()
            res = supabase.table("pedidos").select("total").gte("created_at", f"{today}T00:00:00Z").neq("estado", "CANCELADO").execute()
            return sum(p["total"] for p in res.data)
        except Exception as e:
            raise RepositoryException(f"Error al calcular ventas de hoy: {str(e)}")

    @staticmethod
    def obtener_pedidos_activos() -> int:
        try:
            res = supabase.table("pedidos").select("id", count="exact").neq("estado", "ENTREGADO").neq("estado", "CANCELADO").execute()
            return res.count or 0
        except Exception as e:
            raise RepositoryException(f"Error al contar pedidos activos: {str(e)}")
