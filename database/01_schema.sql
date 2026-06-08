-- 01_schema.sql
-- Inicialización de Esquema para Más Pizzas

-- Habilitar extensión UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- TABLA: usuarios (Usuarios del Panel)
-- ==========================================
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100) UNIQUE NOT NULL,
    rol VARCHAR(50) NOT NULL CHECK (rol IN ('ADMIN', 'GERENTE', 'CAJERO', 'COCINA', 'DELIVERY', 'EMPLEADO')),
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- TABLA: clientes (Clientes de WhatsApp)
-- ==========================================
CREATE TABLE IF NOT EXISTS clientes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(100),
    telefono VARCHAR(20) UNIQUE NOT NULL,
    direccion TEXT,
    ultima_compra TIMESTAMP WITH TIME ZONE,
    preferencias TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- TABLA: productos
-- ==========================================
CREATE TABLE IF NOT EXISTS productos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10, 2) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    imagen_url TEXT,
    activo BOOLEAN DEFAULT true,
    stock_controlado BOOLEAN DEFAULT false,
    stock INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- TABLA: mesas
-- ==========================================
CREATE TABLE IF NOT EXISTS mesas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero INT UNIQUE NOT NULL,
    capacidad INT NOT NULL,
    qr_codigo TEXT,
    activa BOOLEAN DEFAULT true
);

-- ==========================================
-- TABLA: pedidos
-- ==========================================
CREATE TABLE IF NOT EXISTS pedidos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero SERIAL,
    cliente_id UUID REFERENCES clientes(id) ON DELETE SET NULL,
    origen VARCHAR(20) NOT NULL CHECK (origen IN ('WHATSAPP', 'PANEL', 'MESA')),
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'CONFIRMADO', 'EN_PREPARACION', 'LISTO', 'EN_CAMINO', 'ENTREGADO', 'CANCELADO')),
    subtotal DECIMAL(10, 2) DEFAULT 0,
    descuento DECIMAL(10, 2) DEFAULT 0,
    total DECIMAL(10, 2) DEFAULT 0,
    observaciones TEXT,
    fecha_entrega TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- TABLA: pedido_items
-- ==========================================
CREATE TABLE IF NOT EXISTS pedido_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pedido_id UUID REFERENCES pedidos(id) ON DELETE CASCADE,
    producto_id UUID REFERENCES productos(id) ON DELETE RESTRICT,
    cantidad INT NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL
);

-- ==========================================
-- TABLA: reservas
-- ==========================================
CREATE TABLE IF NOT EXISTS reservas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cliente_id UUID REFERENCES clientes(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    cantidad_personas INT NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'REPROGRAMADA')),
    observaciones TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- TABLA: campañas
-- ==========================================
CREATE TABLE IF NOT EXISTS campañas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(100) NOT NULL,
    mensaje TEXT NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'BORRADOR' CHECK (estado IN ('BORRADOR', 'PROGRAMADA', 'EN_PROGRESO', 'COMPLETADA', 'CANCELADA')),
    fecha_programada TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- TABLA: presupuestos_corporativos
-- ==========================================
CREATE TABLE IF NOT EXISTS presupuestos_corporativos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empresa VARCHAR(150) NOT NULL,
    contacto VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100),
    detalle TEXT NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'NUEVO' CHECK (estado IN ('NUEVO', 'ENVIADO', 'APROBADO', 'RECHAZADO')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- TABLA: empleados
-- ==========================================
CREATE TABLE IF NOT EXISTS empleados (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    cargo VARCHAR(100),
    fecha_ingreso DATE,
    activo BOOLEAN DEFAULT true
);

-- ==========================================
-- TABLA: inasistencias
-- ==========================================
CREATE TABLE IF NOT EXISTS inasistencias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    empleado_id UUID REFERENCES empleados(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    motivo TEXT,
    justificada BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- TABLA: auditoria
-- ==========================================
CREATE TABLE IF NOT EXISTS auditoria (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL, 
    accion VARCHAR(50) NOT NULL,
    tabla VARCHAR(50) NOT NULL,
    registro_id UUID,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- FUNCIONES DE AUDITORÍA Y ACTUALIZACIÓN
-- ==========================================

-- Función genérica para actualizar el campo updated_at
CREATE OR REPLACE FUNCTION update_modified_column() 
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers de actualización de timestamps
CREATE TRIGGER update_usuarios_modtime BEFORE UPDATE ON usuarios FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
CREATE TRIGGER update_clientes_modtime BEFORE UPDATE ON clientes FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
CREATE TRIGGER update_productos_modtime BEFORE UPDATE ON productos FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
CREATE TRIGGER update_pedidos_modtime BEFORE UPDATE ON pedidos FOR EACH ROW EXECUTE PROCEDURE update_modified_column();

-- Función genérica para auditar cambios
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
DECLARE
    v_user_id UUID;
BEGIN
    -- Utilizar la función auth.uid() nativa de Supabase para obtener el usuario autenticado.
    -- Si la operación se realiza desde un contexto sin autenticación Supabase (ej: el backend usando service_role), será NULL.
    BEGIN
        v_user_id := auth.uid();
    EXCEPTION WHEN OTHERS THEN
        v_user_id := NULL;
    END;

    IF (TG_OP = 'INSERT') THEN
        INSERT INTO auditoria (usuario_id, accion, tabla, registro_id, payload)
        VALUES (v_user_id, 'INSERT', TG_TABLE_NAME, NEW.id, row_to_json(NEW)::jsonb);
        RETURN NEW;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO auditoria (usuario_id, accion, tabla, registro_id, payload)
        VALUES (v_user_id, 'UPDATE', TG_TABLE_NAME, NEW.id, jsonb_build_object('old', row_to_json(OLD)::jsonb, 'new', row_to_json(NEW)::jsonb));
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        INSERT INTO auditoria (usuario_id, accion, tabla, registro_id, payload)
        VALUES (v_user_id, 'DELETE', TG_TABLE_NAME, OLD.id, row_to_json(OLD)::jsonb);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Función estricta para validar máquina de estados de pedidos
CREATE OR REPLACE FUNCTION validate_pedido_state_transition()
RETURNS TRIGGER AS $$
BEGIN
    -- Permitir actualizaciones si el estado no cambia
    IF OLD.estado = NEW.estado THEN
        RETURN NEW;
    END IF;

    -- Permitir cancelación (salto a CANCELADO)
    IF NEW.estado = 'CANCELADO' THEN
        RETURN NEW;
    END IF;

    -- Máquina de estados obligatoria
    IF OLD.estado = 'PENDIENTE' AND NEW.estado = 'CONFIRMADO' THEN RETURN NEW; END IF;
    IF OLD.estado = 'CONFIRMADO' AND NEW.estado = 'EN_PREPARACION' THEN RETURN NEW; END IF;
    IF OLD.estado = 'EN_PREPARACION' AND NEW.estado = 'LISTO' THEN RETURN NEW; END IF;
    IF OLD.estado = 'LISTO' AND NEW.estado = 'EN_CAMINO' THEN RETURN NEW; END IF;
    IF OLD.estado = 'EN_CAMINO' AND NEW.estado = 'ENTREGADO' THEN RETURN NEW; END IF;

    -- Si no cae en ninguna de las transiciones permitidas, lanzar error bloqueante
    RAISE EXCEPTION 'Transición de estado de pedido inválida: no se permite pasar de % a %', OLD.estado, NEW.estado;
END;
$$ LANGUAGE plpgsql;

-- Trigger para ejecutar la validación ANTES del UPDATE
CREATE TRIGGER enforce_pedidos_state_machine 
BEFORE UPDATE ON pedidos 
FOR EACH ROW EXECUTE PROCEDURE validate_pedido_state_transition();

-- Trigger de auditoría en pedidos
CREATE TRIGGER audit_pedidos_trigger 
AFTER INSERT OR UPDATE OR DELETE ON pedidos 
FOR EACH ROW EXECUTE PROCEDURE audit_trigger_function();


-- ==========================================
-- SEGURIDAD (RLS - Arquitectura Backend-First)
-- ==========================================
-- El RBAC complejo reside en la capa del Backend FastAPI. 
-- Supabase actúa como storage seguro, por lo que bloquearemos todo acceso 
-- directo de modificación desde la API REST pública (anon/authenticated).
-- FastAPI se conectará usando `service_role_key`, lo que automáticamente 
-- sobreescribe y bypassa estas restricciones de RLS.

ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE pedidos ENABLE ROW LEVEL SECURITY;
ALTER TABLE productos ENABLE ROW LEVEL SECURITY;
ALTER TABLE pedido_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE reservas ENABLE ROW LEVEL SECURITY;
ALTER TABLE campañas ENABLE ROW LEVEL SECURITY;
ALTER TABLE presupuestos_corporativos ENABLE ROW LEVEL SECURITY;
ALTER TABLE empleados ENABLE ROW LEVEL SECURITY;
ALTER TABLE inasistencias ENABLE ROW LEVEL SECURITY;
ALTER TABLE auditoria ENABLE ROW LEVEL SECURITY;

-- Única política pública: Permitir lectura del catálogo de productos 
-- (útil para menús QR públicos o catálogos web).
CREATE POLICY "productos_select_public" ON productos 
FOR SELECT USING (true);

-- NOTA: Al no definir políticas para INSERT/UPDATE/DELETE, PostgreSQL aplicará
-- un "Default Deny" estricto. Nadie podrá modificar la base de datos directamente
-- a través de la API REST de Supabase con llaves públicas. Todo el tráfico
-- de mutación deberá pasar obligatoriamente por el Backend FastAPI.
