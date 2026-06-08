from enum import Enum
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr

class RolUsuario(str, Enum):
    ADMIN = "ADMIN"
    GERENTE = "GERENTE"
    CAJERO = "CAJERO"
    COCINA = "COCINA"
    DELIVERY = "DELIVERY"
    EMPLEADO = "EMPLEADO"

class EstadoPedido(str, Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    EN_PREPARACION = "EN_PREPARACION"
    LISTO = "LISTO"
    EN_CAMINO = "EN_CAMINO"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"

class OrigenPedido(str, Enum):
    WHATSAPP = "WHATSAPP"
    PANEL = "PANEL"
    MESA = "MESA"

class Usuario(BaseModel):
    id: Optional[UUID] = None
    nombre: str
    telefono: Optional[str] = None
    email: EmailStr
    rol: RolUsuario
    activo: bool = True

class Cliente(BaseModel):
    id: Optional[UUID] = None
    nombre: Optional[str] = None
    telefono: str
    direccion: Optional[str] = None
    ultima_compra: Optional[datetime] = None
    preferencias: Optional[str] = None

class Producto(BaseModel):
    id: Optional[UUID] = None
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    categoria: str
    imagen_url: Optional[str] = None
    activo: bool = True
    stock_controlado: bool = False
    stock: int = 0

class PedidoItem(BaseModel):
    id: Optional[UUID] = None
    pedido_id: Optional[UUID] = None
    producto_id: UUID
    cantidad: int
    precio_unitario: float
    subtotal: float

class Pedido(BaseModel):
    id: Optional[UUID] = None
    numero: Optional[int] = None
    cliente_id: Optional[UUID] = None
    origen: OrigenPedido
    estado: EstadoPedido = EstadoPedido.PENDIENTE
    subtotal: float = 0.0
    descuento: float = 0.0
    total: float = 0.0
    observaciones: Optional[str] = None
    fecha_entrega: Optional[datetime] = None
    items: Optional[List[PedidoItem]] = []
