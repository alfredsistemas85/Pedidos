from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    app_env: Literal["development", "staging", "production"] = "development"
    backend_url: str
    frontend_url: str
    domain_name: str
    
    supabase_url: str
    supabase_service_role_key: str
    
    evolution_api_url: str
    evolution_api_key: str
    evolution_instance: str
    
    openai_api_key: str
    
    jwt_secret: str
    redis_url: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
