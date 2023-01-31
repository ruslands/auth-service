# # Native # #

# # Installed # #
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

# # Package # #
from app.schemas.team import ICreate, IUpdate
from app.crud.base_sqlmodel import CRUDBase
from app.models.team import Team


class CRUD(CRUDBase[Team, ICreate, IUpdate]):
    async def get_team_by_name(self, db_session: AsyncSession, *, name: str) -> Team:
        team = await db_session.exec(select(Team).where(Team.name == name))
        return team.first()


team = CRUD(Team)
