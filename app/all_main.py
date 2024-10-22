from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi_users import FastAPIUsers, UUIDIDMixin
from fastapi_users.manager import BaseUserManager
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend
from fastapi_users.authentication import BearerTransport
from pydantic import BaseModel
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute
import uuid
from typing import Optional
from fastapi_users import schemas
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter
from passlib.context import CryptContext
from fastapi.concurrency import run_in_threadpool
# Set up logging
import logging
from decouple import config


# Custom auth
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer


print(config('AWS_REGION'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password helper for hashing and verifying passwords
class PasswordHelper:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

# Define the user model using PynamoDB
class UserModel(Model):
    class Meta:
        table_name = "users"
        region = config('AWS_REGION')
        host = config('DATABASE_HOST')
        
        if config('ENVIRONMENT') == 'local':
            host = config('DATABASE_HOST')

    id = UnicodeAttribute(hash_key=True, default=str(uuid.uuid4()))
    email = UnicodeAttribute(null=False)
    hashed_password = UnicodeAttribute(null=False)
    is_active = BooleanAttribute(default=True)
    is_superuser = BooleanAttribute(default=False)
    access_token = UnicodeAttribute(null=True)

# Pydantic models for user schema
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(UserCreate):
    pass

# Custom UserManager with PynamoDB logic
class UserManager(UUIDIDMixin, BaseUserManager[UserModel, uuid.UUID]):
    user_db: UserModel
    password_helper: PasswordHelper

    def __init__(self, user_db, password_helper: PasswordHelper = PasswordHelper()):
        self.user_db = user_db
        self.password_helper = password_helper

    async def validate_password(self, password: str, hashed_password: str) -> bool:
        return self.password_helper.verify(password, hashed_password)

    async def on_after_register(self, user: UserModel, request=None):
        logger.info(f"User {user.email} has registered.")
    
    async def get(self, user_id: uuid.UUID) -> Optional[UserModel]:
    # Convert UUID to string and use run_in_threadpool
        return await run_in_threadpool(UserModel.get, str(user_id))
    
    async def get_by_email(self, user_email: str) -> Optional[UserModel]:
        try:
            result = UserModel.scan(UserModel.email == user_email)
            for user in result:
                return user
        except UserModel.DoesNotExist:
            return None

    async def create(self, user: UserCreate, safe: bool = False, request: Optional[Request] = None) -> UserModel:
        existing_user = await self.get_by_email(user.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists.")
        user_db = UserModel(
            id=str(uuid.uuid4()),
            email=user.email,
            hashed_password=self.password_helper.hash(user.password),
            is_active=True,
            is_superuser=False,
            access_token = None,
        )
        user_db.save()
        return user_db

# JWT Authentication setup
SECRET = "SECRET"

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


# FastAPI app initialization
app = FastAPI()
router = APIRouter()

@app.on_event("startup")
async def on_startup():
    if not UserModel.exists():
        UserModel.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)


fastapi_users = FastAPIUsers[UserModel, uuid.UUID](
    get_user_manager=lambda: UserManager(UserModel),
    auth_backends=[auth_backend],
)


# Custom Auth
# Reuse the Bearer token authentication method
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/jwt/login")

# Custom function to validate current user based on token
async def JWTDBAuthentication(
    token: str = Depends(oauth2_scheme),
    user_manager: UserManager = Depends(get_user_manager),
) -> UserModel:
    """
    Custom build Authentication by combining Database and JWT strategies 
    as mentioned in fastapi_users Stragery
    """
    # Decode the token with the user_manager passed to the JWTStrategy
    jwt_strategy = get_jwt_strategy()
    try:
        user_data = await jwt_strategy.read_token(token, user_manager=user_manager)
        if not user_data:
            raise HTTPException(status_code=401, detail="User Data not found")
    except Exception as e:
        logger.info("Exception on login: %s", str(e))
        raise HTTPException(status_code=401, detail="Invalid token")

    # Fetch the user from the database using the user ID from token
    user_id = user_data.id
    user = await user_manager.get(uuid.UUID(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    # Compare the token with the stored access token in the user model
    if user.access_token != token:
        raise HTTPException(status_code=401, detail="Invalid token or session expired")

    logger.info("Token validated successfully")
    return user

# Private route with custom current_user validation
@router.get("/private", tags=["private"])
async def private_route(current_user: UserModel = Depends(JWTDBAuthentication)):
    return {"message": f"Hello, {current_user.email}! This is a private route."}



# Custom login endpoint
@router.post("/auth/jwt/login", tags=["auth"])
async def custom_login(
    request: Request,
    user_manager=Depends(get_user_manager),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    email = form_data.username
    password = form_data.password

    # Fetch the user from the database
    user = await user_manager.get_by_email(email)

    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # Verify password
    if not await user_manager.validate_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # Create JWT token
    jwt_strategy = get_jwt_strategy()
    token = await jwt_strategy.write_token(user)

    # Store the token in the user's record
    user.access_token = token
    user.update(actions=[UserModel.access_token.set(token)])

    return {"access_token": token, "token_type": "bearer"}



# Custom logout endpoint
@router.post("/auth/jwt/logout", tags=["auth"])
async def logout(current_user: UserModel = Depends(fastapi_users.current_user())):
    # Set access_token to None for the current user
    current_user.access_token = None

    # Save the updated user model in PynamoDB
    current_user.update(actions=[UserModel.access_token.remove()])

    logger.info("User logged out: %s", current_user.email)
    return {"message": "Logged out successfully"}

# Include the routers
app.include_router(router)
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