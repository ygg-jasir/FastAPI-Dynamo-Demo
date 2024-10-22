from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.auth import get_jwt_strategy
from app.managers import UserManager
from app.models import UserModel
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/jwt/login")

async def get_user_manager() -> UserManager:
    return UserManager(UserModel)

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