from contextvars import ContextVar
from typing import Optional

# Context variables to hold request-scoped user information
_current_user_id: ContextVar[Optional[str]] = ContextVar("current_user_id", default=None)
_current_user_role: ContextVar[Optional[str]] = ContextVar("current_user_role", default=None)

def set_current_user(user_id: Optional[str], role: Optional[str]) -> None:
    _current_user_id.set(user_id)
    _current_user_role.set(role)

def get_current_user_id() -> Optional[str]:
    return _current_user_id.get()

def get_current_user_role() -> Optional[str]:
    return _current_user_role.get()

def clear_current_user() -> None:
    _current_user_id.set(None)
    _current_user_role.set(None)
