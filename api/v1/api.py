from fastapi import APIRouter
from api.v1.endpoints import user, auth, sessions, role, team, resource, permission, rbac, visibility_group

__all__ = (
    "router",
)

router = APIRouter()
router.include_router(auth.router, tags=['auth'], prefix="/api/auth/v1")
router.include_router(user.router, tags=['user'], prefix="/api/auth/v1")
router.include_router(sessions.router, tags=['sessions'], prefix="/api/auth/v1")
router.include_router(role.router, tags=['role'], prefix="/api/auth/v1")
router.include_router(team.router, tags=['team'], prefix="/api/auth/v1")
router.include_router(resource.router, tags=['resource'], prefix="/api/auth/v1")
router.include_router(permission.router, tags=['permission'], prefix="/api/auth/v1")
router.include_router(rbac.router, tags=['rbac'], prefix="/api/auth/v1")
router.include_router(visibility_group.router, tags=['visibility_group'], prefix="/api/auth/v1")
