# # Native # #
from typing import List, Optional

# # Installed # #
from sqlmodel import Field, Relationship, SQLModel

# # Package # #
from core.base.model import BaseUUIDModel
from app.common.links import LinkTeamUser

__all__ = (
    "Team",
)


class TeamBase(SQLModel):
    title: str = Field(index=True, sa_column_kwargs={"unique": True})


class Team(BaseUUIDModel, TeamBase, table=True):
    __table_args__ = {
        'comment': 'Team',
        "schema": "auth"
    }
    # users: List["User"] = Relationship(back_populates="team")
    users: Optional[List["User"]] = Relationship(
        back_populates="teams", link_model=LinkTeamUser,
        sa_relationship_kwargs={
            "lazy": "selectin"
        }
    )
