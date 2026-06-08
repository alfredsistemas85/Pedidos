import httpx
from app.core.config import settings
from app.services.ai_provider import OpenAIProvider
from app.services.client_service import ClientService
from app.core.logger import logger

class EvolutionAPIWrapper:
    def __init__(self):
        self.base_url = f"{settings.evolution_api_url}/message"
        self.headers = {
            "apikey": settings.evolution_api_key,
            "Content-Type": "application/json"
        }
        self.instance = settings.evolution_instance

    def enviar_mensaje(self, numero: str, texto: str):
        url = f"{self.base_url}/sendText/{self.instance}"
        payload = {
            "number": numero,
            "text": texto
        }
        try:
            # En producción esto debería ser asíncrono httpx.AsyncClient
            response = httpx.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error enviando mensaje Evolution API a {numero}: {str(e)}")
            return None

class BotService:
    def __init__(self):
        self.evolution = EvolutionAPIWrapper()
        self.ai_provider = OpenAIProvider()
        
    def procesar_webhook(self, payload: dict):
        # 1. Extraer datos del webhook de Evolution API
        try:
            # Simplificación estructural del payload real de Evolution API
            data = payload.get("data", {})
            from_me = data.get("key", {}).get("fromMe", False)
            if from_me:
                return # Ignorar mensajes enviados por el propio bot
                
            remote_jid = data.get("key", {}).get("remoteJid", "")
            if not remote_jid or "@s.whatsapp.net" not in remote_jid:
                return # Ignorar mensajes de grupos o malformados
                
            numero = remote_jid.split("@")[0]
            mensaje_texto = data.get("message", {}).get("conversation", "")
            
            if not mensaje_texto:
                # Intento extraer text_message (extended text)
                mensaje_texto = data.get("message", {}).get("extendedTextMessage", {}).get("text", "")
                
            if not mensaje_texto:
                return # Ignorar medios por ahora
                
            # 2. Registrar cliente
            cliente = ClientService.register_or_get_client(telefono=numero)
            
            # 3. Procesar con IA
            # Contexto mínimo: podríamos pasar historial de Redis aquí
            respuesta_ia = self.ai_provider.process_message(mensaje_texto, [])
            
            # 4. Enviar respuesta por WhatsApp
            self.evolution.enviar_mensaje(numero, respuesta_ia)
            
        except Exception as e:
            logger.error(f"Error procesando webhook: {str(e)}")
