from app.dependencies import JWTDBAuthentication, get_user_manager
from fastapi import APIRouter, Depends, HTTPException, Request
from app.managers import UserManager
from app.auth import auth_backend, get_jwt_strategy
from app.schemas import UserRead, UserCreate, UserUpdate
from fastapi_users import FastAPIUsers
from app.models import UserModel
import uuid
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


fastapi_users = FastAPIUsers[UserModel, uuid.UUID](
    get_user_manager=lambda: UserManager(UserModel),
    auth_backends=[auth_backend],
)

# Register routes
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"]
)


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

    return {
        "access_token": token, 
        "token_type": "bearer",
        "token": "bearer {}".format(token)
    }



# Custom logout endpoint
@router.post("/auth/jwt/logout", tags=["auth"])
async def logout(current_user: UserModel = Depends(fastapi_users.current_user())):
    # Set access_token to None for the current user
    current_user.access_token = None

    # Save the updated user model in PynamoDB
    current_user.update(actions=[UserModel.access_token.remove()])

    logger.info("User logged out: %s", current_user.email)
    return {"message": "Logged out successfully"}

# Private route with custom user validation
@router.get("/private", tags=["private"])
async def private_route(current_user: UserModel = Depends(JWTDBAuthentication)):
    return {"message": f"Hello, {current_user.email}! This is a private route."}