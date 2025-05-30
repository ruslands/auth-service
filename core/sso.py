import httpx
from fastapi_sso.sso.base import OpenID, SSOBase
from integration.keycloak import KeycloakSSO  # noqa

from core.exceptions import UnauthorizedException


async def get_user_info_from_sso_provider(sso_provider: SSOBase, access_token: str) -> OpenID:
    # Get discovery document for SSO provider
    discovery_document = await sso_provider.get_discovery_document()
    userinfo_endpoint = discovery_document["userinfo_endpoint"]
    # Get user data from SSO provider
    async with httpx.AsyncClient() as client:
        response = await client.get(
            userinfo_endpoint,
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        if response.status_code != 200:
            raise UnauthorizedException(detail="Token is invalid")

        user_info = await sso_provider.openid_from_response(response.json())

    return user_info
