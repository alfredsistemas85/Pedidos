from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from app.models.base import CoreModel, DateTimeModelMixin

# Shared properties
class UsuarioBase(CoreModel):
    nombre: str
    telefono: Optional[str] = None
    email: EmailStr
    rol: str
    activo: bool = True

# Properties to receive via API on creation
class UsuarioCreate(UsuarioBase):
    password: str # This won't go directly to DB, it will be hashed

# Properties to receive via API on update
class UsuarioUpdate(UsuarioBase):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    rol: Optional[str] = None
    password: Optional[str] = None
    activo: Optional[bool] = None

# Properties to return to client
class UsuarioResponse(UsuarioBase, DateTimeModelMixin):
    id: UUID

    class Config:
        from_attributes = True

# Token models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
