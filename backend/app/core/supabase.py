from supabase import create_client, Client
from app.core.config import settings
from app.core.logger import logger
import sys

class SupabaseClientManager:
    _instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        if cls._instance is None:
            url = settings.supabase_url
            key = settings.supabase_service_role_key
            
            if not url or not key:
                logger.critical("SUPABASE_URL o SUPABASE_SERVICE_ROLE_KEY faltantes. El Backend DEBE correr con Service Role.")
                sys.exit(1) # Fail fast for production
                
            logger.info("Inicializando Cliente Supabase con Service Role Key (Elevated Privileges)")
            cls._instance = create_client(url, key)
            
        return cls._instance

# Singleton export for Repositories
supabase = SupabaseClientManager.get_client()
