# # Native # #
from datetime import datetime
from uuid import UUID

# # Installed # #
import httpx
from sqlmodel.ext.asyncio.session import AsyncSession

# # Package # #
from app import crud
from core.security import verify_jwt_token
from core.logger import logger
from core.settings import settings
from core.exceptions import ConflictException
from app.visibility_group.schema import IVisibilityGroupSettings

__all__ = ("VisibilityGroup",)


class VisibilityGroup:
    def __init__(self):
        self.visibility = {}
        self.visibility_update_timestamp = 0
        self.VISIBILITY_UPDATE_DELAY = 1  # TODO: increase this to value

    async def get(
        self,
        db_session: AsyncSession,
    ):
        if not self.visibility:
            await self.update(db_session)
            self.visibility_update_timestamp = int(datetime.now().timestamp())
        if (
            int(datetime.now().timestamp()) - self.visibility_update_timestamp
        ) > self.VISIBILITY_UPDATE_DELAY:
            await self.update(db_session)
            self.visibility_update_timestamp = int(datetime.now().timestamp())
        return self.visibility

    async def update(
        self,
        db_session: AsyncSession,
    ):
        self.visibility = await crud.visibility_group.get_visibility_group_and_users(
            db_session
        )
        self.visibility = {
            i.prefix: IVisibilityGroupSettings.parse_obj(i) for i in self.visibility
        }
        # logger.debug(f'Visibility group updated: {self.visibility}')

    async def get_from_api(self):
        async with httpx.ClientSession() as session:
            url = f"{settings.HOSTNAME}/api/vi/visibility_group/settings"
            async with session.get(url) as r:
                r = await r.json()
        return r["data"]

    async def validate(
        self, db_session: AsyncSession, visibility_group_entity: str, access_token: str
    ) -> dict:
        """
        return the list of users whose data can be accessed by the user whose token is passed
        """

        response = {"users": []}

        payload = await verify_jwt_token(token=access_token, token_type="access", db_session=db_session, crud=crud)
        if payload["visibility_group"] is None:
            raise ConflictException(detail="User has no visibility_group")

        visibility_groups = await self.get(db_session)
        if payload["visibility_group"] not in visibility_groups:
            raise ConflictException(
                detail="Visibility group user belongs to does not exist"
            )

        visibility_group = visibility_groups[payload["visibility_group"]].dict()

        logger.debug(f"Visibility groups: {visibility_groups}")
        logger.debug(f"User visibility group: {visibility_group}")

        if visibility_group_entity not in visibility_group:
            raise ConflictException(detail="Visibility group entity does not exist")

        if "admin" in visibility_group[visibility_group_entity] and str(
            visibility_group["admin"]
        ) == str(payload["user_id"]):
            # if user is admin of the visibility group, he can access all the data in this group
            response["users"].extend(visibility_group["user"])

        elif "user" in visibility_group[visibility_group_entity]:
            response["users"].extend(visibility_group["user"])

        elif "owner" in visibility_group[visibility_group_entity]:
            response["users"].extend(
                [{"id": UUID(payload["user_id"]), "email": payload["email"]}]
            )

        # looking for child visibility groups
        for prefix, value in visibility_groups.items():
            if (
                prefix.startswith(visibility_group["prefix"])
                and prefix != visibility_group["prefix"]
            ):
                value = value.dict()
                if "parent" in value[visibility_group_entity]:
                    response["users"].extend(value["user"])

        # looking for parent visibility groups
        parents_prefixes = []
        for i in visibility_group["prefix"].split("/")[:-1]:
            if len(parents_prefixes) == 0:
                parents_prefixes.append(i)
            else:
                parents_prefixes.append(f"{parents_prefixes[-1]}/{i}")
        for prefix, value in visibility_groups.items():
            if prefix in parents_prefixes:
                value = value.dict()
                if "child" in value[visibility_group_entity]:
                    response["users"].extend(value["user"])

        logger.debug(f"Visibility group response: {response}")
        return response
