from app.repositories.product_repository import ProductRepository
from app.domain.models import Producto
from typing import List

class ProductService:
    @staticmethod
    def get_catalog() -> List[Producto]:
        # Aquí se podría añadir lógica de caché con Redis en el futuro
        return ProductRepository.get_all()

    @staticmethod
    def get_product(product_id: str) -> Producto:
        return ProductRepository.get_by_id(product_id)

    @staticmethod
    def create_product(producto: Producto) -> Producto:
        return ProductRepository.create(producto)

    @staticmethod
    def update_product(product_id: str, datos: dict) -> Producto:
        return ProductRepository.update(product_id, datos)

    @staticmethod
    def delete_product(product_id: str) -> Producto:
        return ProductRepository.soft_delete(product_id)
