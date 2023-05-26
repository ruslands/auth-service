# # Native # #

# # Installed # #
from sqladmin import Admin, ModelAdmin

# # Package # #
from core.database.database import async_engine
from app.model import User, Role, Sessions, Resource, Team, Visibility_Group

__all__ = (
    "UserAdmin",
    "RoleAdmin",
    "SessionsAdmin",
    "ResourceAdmin",
    "TeamAdmin",
    "VisibilityGroupAdmin",
)


class UserAdmin(ModelAdmin, model=User):
    name_plural = "Users"
    # column_exclude_list = form_excluded_columns = [
    #     User.title,
    # ]


class RoleAdmin(ModelAdmin, model=Role):
    name_plural = "Roles"


class SessionsAdmin(ModelAdmin, model=Sessions):
    name_plural = "Sessions"


class ResourceAdmin(ModelAdmin, model=Resource):
    name_plural = "Resources"


class TeamAdmin(ModelAdmin, model=Team):
    name_plural = "Teams"


class VisibilityGroupAdmin(ModelAdmin, model=Visibility_Group):
    name_plural = "Visibility Groups"


async def init_admin(app):
    admin = Admin(app, async_engine, base_url="/auth/admin")
    models = [
        UserAdmin,
        RoleAdmin,
        SessionsAdmin,
        TeamAdmin,
        ResourceAdmin,
        VisibilityGroupAdmin,
    ]

    for model in models:
        admin.register_model(model)
