# # Installed # #
import httpx
from fastapi_sso.sso.base import SSOBase, OpenID, SSOLoginError, DiscoveryDocument

# # Package # #
from core.settings import settings


class KeycloakSSO(SSOBase):
    """Class providing login via Keycloak OAuth"""

    discovery_url = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/.well-known/openid-configuration"
    provider = "keycloak"
    scope = ["openid", "email", "profile"]

    @classmethod
    async def openid_from_response(cls, response: dict) -> OpenID:
        """Return OpenID from user information provided by Keycloak"""
        if response.get("email_verified"):
            return OpenID(
                email=response.get("email", ""),
                provider=cls.provider,
                id=response.get("sub"),
                first_name=response.get("given_name"),
                last_name=response.get("family_name"),
                display_name=response.get("name"),
                picture=response.get("picture"),
            )
        raise SSOLoginError(401, f"User {response.get('email')} is not verified with Keycloak")

    async def get_discovery_document(self) -> DiscoveryDocument:
        """Get document containing handy urls"""
        async with httpx.AsyncClient() as session:
            response = await session.get(self.discovery_url)
            content = response.json()
            return content
