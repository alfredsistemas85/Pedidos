class CoreException(Exception):
    """Clase base para todas las excepciones del sistema"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundException(CoreException):
    def __init__(self, resource: str, resource_id: str = None):
        msg = f"{resource} no encontrado" if not resource_id else f"{resource} con id {resource_id} no encontrado"
        super().__init__(msg, 404)

class ValidationException(CoreException):
    def __init__(self, message: str):
        super().__init__(message, 400)

class UnauthorizedException(CoreException):
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, 401)

class ForbiddenException(CoreException):
    def __init__(self, message: str = "Acceso denegado"):
        super().__init__(message, 403)

class StateMachineException(CoreException):
    def __init__(self, entity: str, old_state: str, new_state: str):
        super().__init__(f"Transición de estado inválida para {entity}: no se permite pasar de '{old_state}' a '{new_state}'", 409)

class RepositoryException(CoreException):
    def __init__(self, message: str):
        super().__init__(f"Error en capa de persistencia: {message}", 500)
