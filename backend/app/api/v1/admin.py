from fastapi import APIRouter, Request, HTTPException
from app.core.security import require_role
from app.services.order_service import OrderService

router = APIRouter()

@router.get("/dashboard")
@require_role(["ADMIN", "GERENTE"])
def get_dashboard_stats(request: Request):
    try:
        ventas_hoy = OrderService.obtener_ventas_hoy()
        pedidos_activos = OrderService.obtener_pedidos_activos()
        
        return {
            "ventas_hoy": ventas_hoy,
            "pedidos_activos": pedidos_activos,
            "mensajes_bot": 120 # Fijo por el momento, fuera de alcance MVP
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
