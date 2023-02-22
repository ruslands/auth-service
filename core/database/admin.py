# # Native # #

# # Installed # #
from sqladmin import ModelAdmin

# # Package # #
from app.models import user, role, sessions, resource, team, visibility_group

__all__ = (
    "UserAdmin",
    "RoleAdmin",
    "SessionsAdmin",
    "ResourceAdmin",
    "TeamAdmin",
    "VisibilityGroupAdmin"
)


class UserAdmin(ModelAdmin, model=user.User):
    name_plural = "Users"
    # column_exclude_list = form_excluded_columns = [
    #     User.title,
    # ]


class RoleAdmin(ModelAdmin, model=role.Role):
    name_plural = "Roles"


class SessionsAdmin(ModelAdmin, model=sessions.Sessions):
    name_plural = "Sessions"


class ResourceAdmin(ModelAdmin, model=resource.Resource):
    name_plural = "Resources"


class TeamAdmin(ModelAdmin, model=team.Team):
    name_plural = "Teams"


class VisibilityGroupAdmin(ModelAdmin, model=visibility_group.Visibility_Group):
    name_plural = "Visibility Groups"
