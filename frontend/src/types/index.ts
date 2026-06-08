export interface User {
  id: string;
  email: string;
  role: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  role: string;
}

export interface Product {
  id: string;
  nombre: string;
  descripcion: string;
  precio: number;
  categoria: string;
  imagen_url: string;
  activo: boolean;
  stock_controlado: boolean;
  stock: number;
}

export type OrderStatus = 'PENDIENTE' | 'CONFIRMADO' | 'EN_PREPARACION' | 'LISTO' | 'EN_CAMINO' | 'ENTREGADO' | 'CANCELADO';

export interface OrderItem {
  id: string;
  producto_id: string;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
  producto?: Product; // Expanded field if provided
}

export interface Order {
  id: string;
  numero: number;
  cliente_id: string | null;
  origen: string;
  estado: OrderStatus;
  subtotal: number;
  descuento: number;
  total: number;
  observaciones: string;
  fecha_entrega: string | null;
  created_at: string;
  items?: OrderItem[];
}

export interface DashboardMetrics {
  ventas_hoy: number;
  pedidos_activos: number;
  mensajes_bot: number;
}
