# # Native # #
import re
from datetime import datetime

# # Installed # #
import httpx
from sqlmodel.ext.asyncio.session import AsyncSession

# # Package # #
from app import crud
from core.security import verify_jwt_token
from core.settings import settings
from core.logger import logger
from app.rbac.schema import IRBACValidate, IRBACValidateResponse

__all__ = (
    "RBAC",
)


class RBAC:
    def __init__(self):
        self.rbac = {}
        self.rbac_update_timestamp = 0
        self.RBAC_UPDATE_DELAY = 1  # TODO: increase this to value
        self.patterns = {"$str$": r"[\w.-]+", "$uuid$": r"[\w.-]+"}

    async def get(
        self,
        db_session: AsyncSession,
    ):
        if not self.rbac:
            await self.update(db_session)
            self.rbac_update_timestamp = int(datetime.now().timestamp())
        if (int(datetime.now().timestamp()) - self.rbac_update_timestamp) > self.RBAC_UPDATE_DELAY:
            await self.update(db_session)
            self.rbac_update_timestamp = int(datetime.now().timestamp())
        return self.rbac

    async def update(
        self,
        db_session: AsyncSession,
    ):
        '''
        read database, make rules, save rules to self.rbac
        '''
        data = {"roles": {}, "resources": {}, "permissions": {}}
        roles = await crud.role.get_all(db_session)
        resources = await crud.resource.get_all(db_session)
        permissions = await crud.permission.get_all(db_session)
        for i in roles:
            data['roles'][str(i.id)] = i.title
        for i in resources:
            data['resources'][str(i.id)] = {
                "endpoint": i.endpoint,
                "method": i.method,
                "rbac_enable": i.rbac_enable,
                "visibility_group_enable": i.visibility_group_enable
            }
        for i in permissions:
            data['permissions'][str(i.id)] = {
                "role_id": i.role_id,
                "resource_id": i.resource_id
            }
        for _ in [data['resources'], data['permissions']]:
            for k, v in _.items():
                if not isinstance(k, str) or not isinstance(v, dict):
                    ...
                    # TODO raise error
        self.rbac = data

    async def get_from_api(self):
        async with httpx.ClientSession() as session:
            url = f'{settings.HOSTNAME}/api/rbac'
            async with session.get(url) as r:
                r = await r.json()
        return r['data']

    async def validate(
        self,
        db_session: AsyncSession,
        req: IRBACValidate,
        access_token: str,
    ) -> IRBACValidateResponse:
        logger.debug(f"validate request: {req}")
        payload = await verify_jwt_token(token=access_token, token_type="access", db_session=db_session, crud=crud)
        self.rbac = await self.get(db_session)
        response = {
            "access": True,
            "rbac_enable": False,
            "visibility_group_enable": False,
            "permissions": [],
            "detail": ""
        }
        # find resource_id
        for resource_id, resource in self.rbac['resources'].items():
            if not resource['method'] == req.method:
                continue

            # replace $str$ and $uuid$ with regex.
            endpoint = resource['endpoint']
            for pattern, regexp in self.patterns.items():
                endpoint = endpoint.replace(pattern, regexp)

            logger.debug(f"matching {endpoint} with {req.endpoint}")
            if re.fullmatch(endpoint, req.endpoint):
                logger.debug(f"matched resource: {req.endpoint} {endpoint}")
                response["resource_id"] = resource_id
                response['rbac_enable'] = resource['rbac_enable']
                response['visibility_group_enable'] = resource['visibility_group_enable']
                break

        if "resource_id" not in response:
            response["detail"] = "resource not found"
            logger.debug(
                f"resource not found, hence access allowed; response: {response}")
            return response

        if not response['rbac_enable']:
            response["detail"] = "rbac is disabled"
            logger.debug(
                f"resource was found and rbac is disabled, hence access allowed; response: {response}")
            return response

        # find permissions by user role_id and resource_id
        for _, v in self.rbac['permissions'].items():
            if str(v['role_id']) in payload['roles'] and str(v['resource_id']) == response['resource_id']:
                response['permissions'].append(v)

        if not response['permissions']:
            response['access'] = False
            response["detail"] = "no permissions found"
            logger.debug(
                f"rbac is enabled, no permissions found for the role, hence access denied; response: {response}")
            return response

        response["detail"] = "rbac is enabled, permissions found"
        logger.debug(
            f"rbac is enabled, permissions found for the role, hence access allowed; response: {response}")
        return response
