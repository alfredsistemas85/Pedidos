from fastapi import APIRouter, Request, HTTPException
from app.services.product_service import ProductService
from app.core.security import require_role
from app.domain.models import Producto
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ProductCreateRequest(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    categoria: str
    imagen_url: Optional[str] = None
    stock_controlado: bool = False
    stock: int = 0

class ProductUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    categoria: Optional[str] = None
    imagen_url: Optional[str] = None
    activo: Optional[bool] = None
    stock_controlado: Optional[bool] = None
    stock: Optional[int] = None

@router.get("/")
def get_products():
    return ProductService.get_catalog()

@router.get("/{product_id}")
def get_product(product_id: str):
    product = ProductService.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@router.post("/")
@require_role(["ADMIN", "GERENTE"])
def create_product(request: Request, payload: ProductCreateRequest):
    try:
        nuevo_producto = Producto(**payload.model_dump())
        return ProductService.create_product(nuevo_producto)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{product_id}")
@require_role(["ADMIN", "GERENTE"])
def update_product(request: Request, product_id: str, payload: ProductUpdateRequest):
    try:
        datos_actualizar = payload.model_dump(exclude_unset=True)
        producto_actualizado = ProductService.update_product(product_id, datos_actualizar)
        if not producto_actualizado:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return producto_actualizado
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{product_id}")
@require_role(["ADMIN", "GERENTE"])
def delete_product(request: Request, product_id: str):
    try:
        producto_borrado = ProductService.delete_product(product_id)
        if not producto_borrado:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return {"message": "Producto eliminado correctamente", "producto": producto_borrado}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
