from fastapi_users import schemas
from typing import Optional
import uuid


# Schema
class UserRead(schemas.BaseUser[uuid.UUID]):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(UserCreate):
    pass
