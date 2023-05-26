# # Native # #

# # Installed # #
from sqlmodel import select, and_
from sqlmodel.ext.asyncio.session import AsyncSession

# # Package # #
from app.resource.schema import ICreate, IUpdate
from app.resource.model import Resource
from core.base.crud import CRUDBase
from core.settings import settings


class CRUD(CRUDBase[Resource, ICreate, IUpdate]):
    async def get_resource_by_endpoint_and_method(
        self, db_session: AsyncSession, *, endpoint: str, method: str
    ) -> Resource:
        endpoint = endpoint.replace(settings.HOSTNAME, "")
        method = method.lower()
        resource = await db_session.exec(
            select(Resource).where(
                and_(Resource.endpoint == endpoint, Resource.method == method)
            )
        )
        return resource.first()


resource = CRUD(Resource)
