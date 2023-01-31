# # Native # #

# # Installed # #
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

# # Package # #
from app.schemas.sessions import ICreate, IUpdate
from app.crud.base_sqlmodel import CRUDBase
from app.models.sessions import Sessions


class CRUD(CRUDBase[Sessions, ICreate, IUpdate]):
    async def create(self, db_session: AsyncSession, *, obj_in: ICreate) -> Sessions:
        db_obj = obj_in
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def get_by_access_token(self, db_session: AsyncSession, *, access_token: str) -> Sessions:
        sessions = await db_session.exec(select(Sessions).where(Sessions.access_token == access_token))
        return sessions.first()

    async def get_by_refresh_token(self, db_session: AsyncSession, *, refresh_token: str) -> Sessions:
        sessions = await db_session.exec(select(Sessions).where(Sessions.refresh_token == refresh_token))
        return sessions.first()


sessions = CRUD(Sessions)
