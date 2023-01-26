# # Native # #
import json


# # Installed # #
import jwt
from passlib.context import CryptContext
# from sqlmodel.ext.asyncio.session import AsyncSession

# # Package # #
from settings import settings
from logger import logger
from exceptions import UnauthorizedException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

__all__ = (
    "verify_jwt_token",
)


def verify_jwt_token(token: str) -> dict:
    try:
        if 'Bearer' in token:
            token = token.replace('Bearer', '').strip()
        payload = jwt.decode(token, settings.PEM_PUBLIC_KEY,
                             algorithms=["RS256"])
        logger.info(f'payload: {payload}')
        if payload['type'] != "access":
            raise UnauthorizedException(detail="Invalid token type")

        payload = json.loads(payload['sub'])

        if not set(["user_id", "roles", "teams", "visibility_group", "email", "region"]).issubset(payload.keys()):
            raise UnauthorizedException(detail="Invalid token payload")

        if not isinstance(payload['roles'], dict):
            raise UnauthorizedException(detail="Invalid token payload roles")

        # if not await crud.sessions.get_by_access_token(db_session, access_token=token):
        #     raise UnauthorizedException(detail="Access token not found")

        return payload

    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(detail="Token expired")
    except UnauthorizedException:
        raise
    except Exception as e:
        raise UnauthorizedException(detail=f"Invalid token: {e}")
