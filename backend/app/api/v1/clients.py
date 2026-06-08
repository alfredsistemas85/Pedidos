from fastapi import APIRouter, Request, HTTPException
from app.services.client_service import ClientService
from app.core.security import require_role
from pydantic import BaseModel

router = APIRouter()

class PreferencesUpdate(BaseModel):
    preferencias: str

@router.patch("/{cliente_id}/preferences")
@require_role(["ADMIN", "GERENTE", "CAJERO"])
def update_preferences(request: Request, cliente_id: str, payload: PreferencesUpdate):
    try:
        return ClientService.update_preferences(cliente_id, payload.preferencias)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
