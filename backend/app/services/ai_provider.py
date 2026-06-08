from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import openai
from app.core.config import settings

class AIProvider(ABC):
    @abstractmethod
    def process_message(self, message: str, context: list) -> str:
        pass
        
    @abstractmethod
    def classify_intent(self, message: str) -> str:
        pass
        
    @abstractmethod
    def extract_order(self, message: str) -> Tuple[bool, Dict[str, Any]]:
        pass
        
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

class OpenAIProvider(AIProvider):
    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.model = "gpt-4o"
        
    def process_message(self, message: str, context: list) -> str:
        # Implementación real de NLP
        messages = [{"role": "system", "content": "Eres un asistente de la pizzería Más Pizzas."}]
        messages.extend(context)
        messages.append({"role": "user", "content": message})
        
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return "Lo siento, tuve un problema procesando tu mensaje. ¿Podrías repetirlo?"

    def classify_intent(self, message: str) -> str:
        # Determina si es PEDIDO, CONSULTA_MENU, QUEJA, etc.
        # Simplificado para la estructura
        return "PEDIDO"

    def extract_order(self, message: str) -> Tuple[bool, Dict[str, Any]]:
        # Extraería JSON con los items del pedido usando function calling
        return False, {}

    def generate_response(self, prompt: str) -> str:
        return self.process_message(prompt, [])
