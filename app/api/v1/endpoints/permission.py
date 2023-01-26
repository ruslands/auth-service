# # Native # #
from uuid import UUID

# # Installed # #
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends

# # Package # #
from app.utils.settings import Params, Page
from app.utils.exceptions import AlreadyExistsException, NotFoundException
from app import crud
from app.database.user import get_current_user
from app.database.session import get_session
from app.models.user import User
from app.schemas.permission import IPermissionCreate, IPermissionRead, IPermissionUpdate
from app.schemas.common import (
    IGetResponseBase,
    IPostResponseBase,
    IPutResponseBase,
    IDeleteResponseBase
)

router = APIRouter()


@router.get("/permission/list", response_model=IGetResponseBase[Page[IPermissionRead]])
async def get_permissions(
    params: Params = Depends(),
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    permissions = await crud.permission.get_multi_paginated(db_session, params=params)
    return IGetResponseBase[Page[IPermissionRead]](data=permissions)


@router.get("/permission/{permission_id}", response_model=IGetResponseBase[IPermissionRead])
async def get_permission_by_id(
    permission_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user()),
):
    permission = await crud.permission.get(db_session, id=permission_id)
    return IGetResponseBase[IPermissionRead](data=permission)


@router.post("/permission", response_model=IPostResponseBase[IPermissionRead])
async def create_permission(
    new_permission: IPermissionCreate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    if await crud.permission.get_permission_by_resource_id_role_id(db_session, permission=new_permission):
        raise AlreadyExistsException
    new_permission = await crud.permission.create(db_session, obj_in=new_permission)
    return IPostResponseBase[IPermissionRead](data=new_permission)


@router.patch("/permission/{permission_id}", response_model=IPutResponseBase[IPermissionRead])
async def update_permission(
    permission_id: UUID,
    permission: IPermissionUpdate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    current_permission = await crud.permission.get(db_session=db_session, id=permission_id)
    if not current_permission:
        raise NotFoundException

    updated_permission = await crud.permission.update(db_session, obj_current=current_permission, obj_new=permission)
    return IPutResponseBase[IPermissionRead](data=updated_permission)


@router.delete("/permission/{permission_id}", response_model=IGetResponseBase[IPermissionRead])
async def delete_permission_by_id(
    permission_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    permission = await crud.permission.get(db_session=db_session, id=permission_id)
    if not permission:
        raise NotFoundException
    permission = await crud.permission.remove(db_session, id=permission_id)
    return IDeleteResponseBase[IPermissionRead](
        data=permission
    )
