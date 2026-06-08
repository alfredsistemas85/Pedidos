-- 02_auth_fix.sql
-- Actualización crítica de seguridad para Fase 1.7

-- Añadir columna para contraseña hasheada (bcrypt)
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) DEFAULT NULL;

-- Asegurar que las políticas de seguridad mantengan la consistencia
-- Solo el rol service_role (usado por el backend) puede ver/escribir password_hash
-- (En Supabase las políticas RLS por defecto se aplican si la tabla tiene habilitado RLS)
