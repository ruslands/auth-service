# # Native # #
from uuid import UUID

# # Installed # #
from sqlmodel import Field, SQLModel

# # Package # #


class LinkRoleUser(SQLModel, table=True):
    role_id: UUID = Field(default=None, nullable=False,
                          foreign_key="role.id", primary_key=True)
    user_id: UUID = Field(default=None, nullable=False,
                          foreign_key="user.id", primary_key=True)


class LinkTeamUser(SQLModel, table=True):
    team_id: UUID = Field(default=None, nullable=False,
                          foreign_key="team.id", primary_key=True)
    user_id: UUID = Field(default=None, nullable=False,
                          foreign_key="user.id", primary_key=True)
