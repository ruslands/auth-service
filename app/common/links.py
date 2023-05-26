# # Native # #
from uuid import UUID

# # Installed # #
from sqlmodel import Field, SQLModel

# # Package # #


class LinkRoleUser(SQLModel, table=True):
    __table_args__ = {
        'comment': 'Link Role User',
        "schema": "auth"
    }
    role_id: UUID = Field(default=None, nullable=False,
                          foreign_key="auth.role.id", primary_key=True)
    user_id: UUID = Field(default=None, nullable=False,
                          foreign_key="auth.user.id", primary_key=True)


class LinkTeamUser(SQLModel, table=True):
    __table_args__ = {
        'comment': 'Link Team User',
        "schema": "auth"
    }
    team_id: UUID = Field(default=None, nullable=False,
                          foreign_key="auth.team.id", primary_key=True)
    user_id: UUID = Field(default=None, nullable=False,
                          foreign_key="auth.user.id", primary_key=True)
