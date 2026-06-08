from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List
from app.services.order_service import OrderService
from app.domain.models import Pedido, PedidoItem
from app.core.security import require_role

router = APIRouter()

class CreateOrderRequest(BaseModel):
    pedido: Pedido
    items: List[PedidoItem]

class UpdateStatusRequest(BaseModel):
    estado: str

@router.get("/")
@require_role(["ADMIN", "GERENTE", "CAJERO"])
def get_orders(request: Request, page: int = 1, limit: int = 50):
    try:
        limit = min(limit, 100) # Máximo permitido
        return OrderService.get_orders(page, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{pedido_id}")
@require_role(["ADMIN", "GERENTE", "CAJERO", "COCINA", "DELIVERY"])
def get_order(request: Request, pedido_id: str):
    try:
        pedido = OrderService.get_order(pedido_id)
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return pedido
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/")
@require_role(["ADMIN", "GERENTE", "CAJERO"])
def create_order(request: Request, payload: CreateOrderRequest):
    try:
        return OrderService.create_order(payload.pedido, payload.items)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{pedido_id}/status")
@require_role(["ADMIN", "GERENTE", "CAJERO", "COCINA", "DELIVERY"])
def update_status(request: Request, pedido_id: str, payload: UpdateStatusRequest):
    try:
        return OrderService.update_status(pedido_id, payload.estado)
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))
