from app.repositories.order_repository import OrderRepository
from app.domain.models import Pedido, PedidoItem, EstadoPedido
from app.core.exceptions import StateMachineException, ValidationException
from typing import List

class OrderService:
    # Definición estricta de máquina de estados en el backend
    VALID_TRANSITIONS = {
        EstadoPedido.PENDIENTE: [EstadoPedido.CONFIRMADO, EstadoPedido.CANCELADO],
        EstadoPedido.CONFIRMADO: [EstadoPedido.EN_PREPARACION, EstadoPedido.CANCELADO],
        EstadoPedido.EN_PREPARACION: [EstadoPedido.LISTO, EstadoPedido.CANCELADO],
        EstadoPedido.LISTO: [EstadoPedido.EN_CAMINO, EstadoPedido.CANCELADO],
        EstadoPedido.EN_CAMINO: [EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO],
        EstadoPedido.ENTREGADO: [],
        EstadoPedido.CANCELADO: []
    }

    @staticmethod
    def create_order(pedido: Pedido, items: List[PedidoItem]) -> Pedido:
        if not items:
            raise ValidationException("El pedido debe tener al menos un item.")
            
        # Calcular totales para evitar manipulación del frontend
        subtotal = sum(item.precio_unitario * item.cantidad for item in items)
        pedido.subtotal = subtotal
        pedido.total = subtotal - pedido.descuento
        pedido.estado = EstadoPedido.PENDIENTE
        
        return OrderRepository.create(pedido, items)

    @staticmethod
    def update_status(pedido_id: str, nuevo_estado: str) -> Pedido:
        pedido_actual = OrderRepository.get_by_id(pedido_id)
        if not pedido_actual:
            raise ValidationException("Pedido no encontrado")
            
        estado_actual = pedido_actual.estado
        nuevo_estado_enum = EstadoPedido(nuevo_estado)
        
        if nuevo_estado_enum not in OrderService.VALID_TRANSITIONS.get(estado_actual, []):
            if estado_actual != nuevo_estado_enum: # Permitir update si es el mismo estado
                raise StateMachineException("Pedido", estado_actual, nuevo_estado)
                
        return OrderRepository.update_status(pedido_id, nuevo_estado)
        
    @staticmethod
    def assign_delivery(pedido_id: str) -> Pedido:
        # Lógica para asignar repartidor
        return OrderService.update_status(pedido_id, EstadoPedido.EN_CAMINO)

    @staticmethod
    def get_orders(page: int = 1, limit: int = 50) -> dict:
        return OrderRepository.get_all_paginated(page, limit)

    @staticmethod
    def get_order(pedido_id: str) -> Pedido:
        return OrderRepository.get_by_id(pedido_id)

    @staticmethod
    def obtener_ventas_hoy() -> float:
        return OrderRepository.obtener_ventas_hoy()

    @staticmethod
    def obtener_pedidos_activos() -> int:
        return OrderRepository.obtener_pedidos_activos()
