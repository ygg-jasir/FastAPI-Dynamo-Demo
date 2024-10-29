from typing import List
from app.dependencies import JWTDBAuthentication, get_user_manager
from fastapi import APIRouter, Depends, HTTPException, Request
from app.managers import UserManager
from app.auth import auth_backend, get_access_token_strategy, get_jwt_strategy, get_refresh_token_strategy, cookie_transport
from app.schemas import UserRead, UserCreate, UserUpdate
from fastapi_users import FastAPIUsers
from app.models import UserModel
import uuid
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import logging
from fastapi.responses import JSONResponse

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

    # Create JWT access_token
    jwt_strategy = get_access_token_strategy()
    access_token = await jwt_strategy.write_token(user)
    
    # Create refresh token
    refresh_token = await get_refresh_token_strategy().write_token(user)

    # Store the token in the user's record
    user.access_token = access_token
    user.refresh_token = refresh_token
    user.update(
        actions=[
            UserModel.access_token.set(access_token),
            UserModel.refresh_token.set(refresh_token)
            ]
        )
    response = JSONResponse({
        "message": "Login Success", 
        "user_id": user.id,
        "access_token": "bearer {}".format(access_token),
        "refresh_token": refresh_token
        })
    
    cookie_transport._set_login_cookie(response, refresh_token)

    return response


# Custom logout endpoint
@router.post("/auth/jwt/logout", tags=["auth"])
async def logout(current_user: UserModel = Depends(fastapi_users.current_user())):
    print("logout ")
    # Set tokens to None for the current user
    current_user.access_token = None
    current_user.refresh_token = None

    # Save the updated user model in PynamoDB
    current_user.update(actions=[
        UserModel.access_token.remove(),
        UserModel.refresh_token.remove()
        ])
    response = JSONResponse({"message": "Logged out successfully"})

    cookie_transport._set_logout_cookie(response)
    logger.info("User logged out: %s", current_user.email)
    return response


@router.post("/auth/jwt/refresh", tags=["auth"])
async def refresh_token(request: Request, user_manager=Depends(get_user_manager)):
    refresh_token = request.cookies.get("refresh_token")
    print(refresh_token)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    jwt_strategy = get_refresh_token_strategy()
    try:
        # Decode and validate the refresh token
        user_data = await jwt_strategy.read_token(refresh_token, user_manager=user_manager)
        user = await user_manager.get(user_data.id)
        if not user or user.refresh_token != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Generate new access token
    new_access_token = await get_access_token_strategy().write_token(user)
    user.access_token = new_access_token
    user.update(actions=[UserModel.access_token.set(new_access_token)])

    return {"token_type": "{}".format(new_access_token)}


# @router.get("/users/", tags=["users"], response_model=List[UserRead])
# async def list_users_route(
#     current_user: UserModel = Depends(fastapi_users.current_user(active=True)),
#     user_manager: UserManager = Depends(get_user_manager),
# ):
#     print(current_user)
#     # Ensure the current user has permission (e.g., is a superuser)
#     if not current_user.is_superuser:
#         raise HTTPException(status_code=403, detail="Insufficient permissions")

#     # Fetch all users
#     users = await user_manager.list_users()
#     return users

@router.get("/users-list", tags=["users"],)
async def list_users_route():
    print("List usre")
    # Fetch all users from the UserModel table
    result = UserModel.scan()
    users = [user for user in result]
    return users


# Private route with custom user validation
@router.get("/private", tags=["private"])
async def private_route(current_user: UserModel = Depends(JWTDBAuthentication)):
    return {"message": f"Hello, {current_user.email}! This is a private route."}