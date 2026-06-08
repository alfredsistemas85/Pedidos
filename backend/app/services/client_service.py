from app.repositories.client_repository import ClientRepository
from app.domain.models import Cliente
from typing import Optional

class ClientService:
    @staticmethod
    def register_or_get_client(telefono: str, nombre: Optional[str] = None) -> Cliente:
        # Check if exists
        cliente = ClientRepository.get_by_phone(telefono)
        if cliente:
            # Update name if provided and missing
            if nombre and not cliente.nombre:
                cliente = ClientRepository.update(str(cliente.id), {"nombre": nombre})
            return cliente
            
        # Create new
        nuevo_cliente = Cliente(telefono=telefono, nombre=nombre)
        return ClientRepository.create(nuevo_cliente)
        
    @staticmethod
    def update_preferences(cliente_id: str, preferencias: str) -> Cliente:
        return ClientRepository.update(cliente_id, {"preferencias": preferencias})
