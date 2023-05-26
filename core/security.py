# # Native # #
import json
import random
import string
from datetime import datetime, timedelta


# # Installed # #
import jwt
from passlib.context import CryptContext
from sqlmodel.ext.asyncio.session import AsyncSession

# # Package # #
from core.settings import settings
from core.logger import logger
from core.exceptions import UnauthorizedException
# from app import crud

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

__all__ = (
    "create_cookie",
    "create_jwt_token",
    "verify_jwt_token",
    "create_password",
    "get_password_hash",
    "verify_password",
)


def create_cookie():
    return pwd_context.hash(''.join(random.choice(string.ascii_letters) for i in range(150)))


def create_jwt_token(subject: dict, expires_delta: timedelta, token_type: str) -> str:
    # expire = datetime.utcnow() + expires_delta
    expire = int((datetime.utcnow() + expires_delta).timestamp())
    to_encode = {"exp": expire, "sub": json.dumps(subject), "type": token_type}
    encoded_jwt = jwt.encode(to_encode, settings.PEM_PRIVATE_KEY, algorithm="RS256")
    return encoded_jwt, expire


async def verify_jwt_token(token: str, token_type: str, db_session: AsyncSession, crud) -> dict:
    try:
        payload = jwt.decode(token, settings.PEM_PUBLIC_KEY,
                             algorithms=["RS256"], options={"verify_exp": True})
        logger.info(f'jwt payload: {payload}')
        if payload['type'] not in ["access", "refresh"]:
            raise UnauthorizedException(detail="Invalid token type")
        payload = json.loads(payload['sub'])
        if token_type == "access":
            if not set(["user_id", "roles", "teams", "visibility_group"]).issubset(payload.keys()):
                raise UnauthorizedException(detail="Invalid token payload")
            if not isinstance(payload['roles'], dict):
                raise UnauthorizedException(detail="Invalid token payload roles")
            if not await crud.sessions.get_by_access_token(db_session, access_token=token):
                raise UnauthorizedException(detail="Access token not found")
            return payload
        elif token_type == "refresh":
            if not set(["user_id"]).issubset(payload.keys()):
                raise UnauthorizedException(detail="Invalid token payload")
            if not await crud.sessions.get_by_refresh_token(db_session, refresh_token=token):
                raise UnauthorizedException(detail="Refresh token not found")
            return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(detail="Token expired")
    except UnauthorizedException:
        raise
    except Exception as e:
        raise UnauthorizedException(detail=f"Invalid token: {e}")


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(e)
        return False


def create_password():
    return ''.join(random.choice(string.ascii_letters) for i in range(15))


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
