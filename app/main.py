from fastapi import FastAPI, Depends
from fastapi_users import FastAPIUsers, BaseUserManager, UUIDIDMixin
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend
from fastapi_users.authentication import BearerTransport
from pydantic import BaseModel
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute
import uuid
from typing import Optional
from fastapi_users import schemas
from fastapi import Request 

# Define the user model using PynamoDB
class UserModel(Model):
    class Meta:
        table_name = "users"
        region = "us-east-1"  # Adjust as per your DynamoDB region
        host = "http://localhost:8000"  # Set this to DynamoDB local for development, remove for production

    id = UnicodeAttribute(hash_key=True, default=str(uuid.uuid4()))
    email = UnicodeAttribute(null=False)
    hashed_password = UnicodeAttribute(null=False)
    is_active = BooleanAttribute(default=True)
    is_superuser = BooleanAttribute(default=False)

# Pydantic models
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(UserCreate):
    pass

# Custom UserManager
class UserManager(UUIDIDMixin, BaseUserManager[UserModel, uuid.UUID]):
    user_db_model = UserModel

    async def get(self, user_id: uuid.UUID) -> Optional[UserModel]:
        try:
            # Convert UUID to a string before querying DynamoDB
            return UserModel.get(str(user_id))
        except UserModel.DoesNotExist:
            return None

    async def get_by_email(self, user_email: str) -> Optional[UserModel]:
        try:
            result = UserModel.scan(UserModel.email == user_email)
            for user in result:
                return user
        except UserModel.DoesNotExist:
            return None
        return None

    async def create(self, user: UserCreate, safe: bool = False, request: Optional[Request] = None) -> UserModel:
        user_db = UserModel(
            id=str(uuid.uuid4()),  # Ensure ID is stored as a string
            email=user.email,
            hashed_password=self.password_helper.hash(user.password),
            is_active=True,
            is_superuser=False,
        )
        user_db.save()
        return user_db


    async def validate_password(self, password: str, user: UserCreate) -> None:
        # Add custom password validation logic here
        pass

    async def on_after_register(self, user: UserModel, request: Optional[FastAPI] = None):
        print(f"User {user.email} has registered.")

# JWT Authentication
SECRET = "SECRET"

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# FastAPI setup
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    # Ensure PynamoDB table exists
    if not UserModel.exists():
        UserModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

# Function to get user manager
async def get_user_manager() -> UserManager:
    return UserManager(UserModel)

# Initialize FastAPI Users
fastapi_users = FastAPIUsers(
    get_user_manager=get_user_manager,  # Call the function instead of passing the instance
    auth_backends=[auth_backend],
)

# Routes for auth and users
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"]
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to FastAPI with DynamoDB!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)