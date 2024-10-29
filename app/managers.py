import uuid
from app.models import UserModel
from app.schemas import UserCreate
from fastapi_users.manager import BaseUserManager, UUIDIDMixin
from fastapi.concurrency import run_in_threadpool
from passlib.context import CryptContext
from fastapi import HTTPException, Request
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PasswordHelper:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

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
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            access_token=None,
        )
        user_db.save()
        return user_db
            
    async def list_users(self) -> List[UserModel]:
        result = UserModel.scan()
        users = [user for user in result]
        return users