from fastapi_users import schemas
import uuid


# Schema
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(UserCreate):
    pass
