# # Native # #
from uuid import UUID

# # Installed # #
import sqlalchemy
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends

# # Package # #
from app.utils.settings import Params, Page
from app.utils.logger import logger
from app.utils.exceptions import AlreadyExistsException, NotFoundException, BadRequestException
from app import crud
from app.database.user import get_current_user
from app.database.session import get_session
from app.models.user import User
from app.schemas.role import IRoleCreate, IRoleRead, IRoleUpdate, IRoleReadWithPermissions
from app.schemas.common import (
    IGetResponseBase,
    IPostResponseBase,
    IPutResponseBase,
    IDeleteResponseBase
)

router = APIRouter()


@router.get("/role/list", response_model=IGetResponseBase[Page[IRoleRead]])
async def get_roles(
    params: Params = Depends(),
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user()),
):
    roles = await crud.role.get_multi_paginated(db_session, params=params)
    return IGetResponseBase[Page[IRoleRead]](data=roles)


@router.get("/role/{role_id}", response_model=IGetResponseBase[IRoleReadWithPermissions])
async def get_role_by_id(
    role_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user()),
):
    role = await crud.role.get(db_session, id=role_id)
    logger.debug(role)
    return IGetResponseBase[IRoleReadWithPermissions](data=role)


@router.post("/role", response_model=IPostResponseBase[IRoleRead])
async def create_role(
    new_role: IRoleCreate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    if await crud.role.get_role_by_name(db_session, name=new_role.name):
        raise AlreadyExistsException
    new_role = await crud.role.create(db_session, obj_in=new_role)
    return IPostResponseBase[IRoleRead](data=new_role)


@router.patch("/role/{role_id}", response_model=IPutResponseBase[IRoleRead])
async def update_role(
    role_id: UUID,
    role: IRoleUpdate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    current_role = await crud.role.get(db_session=db_session, id=role_id)
    if not current_role:
        raise NotFoundException
    role.updated_by = current_user.id
    try:
        updated_role = await crud.role.update(db_session, obj_current=current_role, obj_new=role)
    except sqlalchemy.exc.IntegrityError as e:
        raise BadRequestException(detail=f"Role update failed: {e}")
    return IPutResponseBase[IRoleRead](data=updated_role)


@router.delete("/role/{role_id}", response_model=IGetResponseBase[IRoleRead])
async def delete_role_by_id(
    role_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    role = await crud.role.get(db_session=db_session, id=role_id)
    if not role:
        raise NotFoundException
    role = await crud.role.remove(db_session, id=role_id)
    return IDeleteResponseBase[IRoleRead](
        data=role
    )
