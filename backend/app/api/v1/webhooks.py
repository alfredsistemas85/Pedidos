from fastapi import APIRouter, Request
from app.services.bot_service import BotService

router = APIRouter()
bot_service = BotService()

@router.post("/evolution")
async def evolution_webhook(request: Request):
    payload = await request.json()
    # Ejecutar procesamiento del bot
    # En un entorno de alto tráfico esto debería enviarse a Celery o BackgroundTasks
    bot_service.procesar_webhook(payload)
    return {"status": "received"}
