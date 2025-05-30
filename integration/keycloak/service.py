import httpx
from fastapi_sso.sso.base import (
    DiscoveryDocument,
    OpenID,
    SSOBase,
    SSOLoginError,
)

from core.settings import settings


class KeycloakSSO(SSOBase):
    """Class providing login via Keycloak OAuth"""

    discovery_url = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/.well-known/openid-configuration"
    provider = "keycloak"
    scope = ["openid", "email", "profile"]

    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:
        """Return OpenID from user information provided by Keycloak"""
        if not response.get("email_verified"):
            raise SSOLoginError(401, f"User {response.get('email')} is not verified with Keycloak")

        return OpenID(
            email=response.get("email", ""),
            provider=cls.provider,
            id=response.get("sub"),
            first_name=response.get("given_name"),
            last_name=response.get("family_name"),
            display_name=response.get("name"),
            picture=response.get("picture"),
        )

    async def get_discovery_document(self) -> DiscoveryDocument:
        """Get document containing handy urls"""
        async with httpx.AsyncClient() as session:
            response = await session.get(self.discovery_url)
            return response.json()
