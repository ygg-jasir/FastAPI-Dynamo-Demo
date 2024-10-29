from fastapi_users.authentication import JWTStrategy, AuthenticationBackend, BearerTransport
from fastapi_users.authentication import CookieTransport

SECRET = "SECRET"

# Constants for token lifetime
ACCESS_TOKEN_LIFETIME = 3600  # 1 hour
REFRESH_TOKEN_LIFETIME = 24 * 3600 * 7  # 7 days

# Update JWT Strategy to support refresh token
def get_access_token_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=ACCESS_TOKEN_LIFETIME)

def get_refresh_token_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=REFRESH_TOKEN_LIFETIME)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=ACCESS_TOKEN_LIFETIME)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
# Cookie transport for storing refresh token
cookie_transport = CookieTransport(cookie_max_age=REFRESH_TOKEN_LIFETIME, cookie_name="refresh_token", cookie_httponly=True)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
