# # Native # #

# # Installed # #
from sqlmodel import select, and_
from sqlmodel.ext.asyncio.session import AsyncSession

# # Package # #
from app.schemas.resource import IResourceCreate, IResourceUpdate
from app.models.resource import Resource
from app.crud.base_sqlmodel import CRUDBase
from app.utils.settings import settings


class CRUDResource(CRUDBase[Resource, IResourceCreate, IResourceUpdate]):
    async def get_resource_by_endpoint_and_method(self, db_session: AsyncSession, *, endpoint: str, method: str) -> Resource:
        endpoint = endpoint.replace(settings.HOSTNAME, "")
        method = method.lower()
        resource = await db_session.exec(select(Resource).where(and_(Resource.endpoint == endpoint, Resource.method == method)))
        return resource.first()


resource = CRUDResource(Resource)
