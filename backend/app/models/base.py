from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class CoreModel(BaseModel):
    """
    Any common logic to be shared by all models goes here.
    """
    pass

class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
