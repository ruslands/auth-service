# # Native # #
from uuid import UUID

# # Installed # #
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends

# # Package # #
from core.settings import Params, Page
from core.exceptions import AlreadyExistsException, NotFoundException
from app import crud
from app.user.util import get_current_user
from core.database.session import get_session
from app.model import User
from app.permission.schema import ICreate, IRead, IUpdate, IFilter
from core.base.schema import (
    IGetResponseBase,
    IPostResponseBase,
    IPutResponseBase,
    IDeleteResponseBase
)
from core.utils import ColumnAnnotation, ApiListUtils

router = APIRouter()

utils = ApiListUtils(IFilter, IRead)

@router.get("/permission/list", response_model=IGetResponseBase[Page[IRead]], response_model_exclude_none=True)
async def list(
    params: Params = Depends(),
    db_session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user()),
    filters: dict = Depends(utils.filters),
    scope: set = Depends(utils.scope)
):
    meta = {
        "table_name": "permission",
        "table_mapping": [
            ColumnAnnotation(column_name="id", key_name="id"),
            ColumnAnnotation(column_name="обновлено", key_name="updated_at", column_type="datetime"),
            ColumnAnnotation(column_name="создано", key_name="created_at", column_type="datetime"),
            ColumnAnnotation(column_name="обновил", key_name="updated_by"),
            ColumnAnnotation(column_name="создал", key_name="created_by"),
            ColumnAnnotation(column_name="пермишен", key_name="name", default_visibility=True),
            ColumnAnnotation(column_name="описание", key_name="description", default_visibility=True)
        ]
    }
    permissions = await crud.permission.get_multi_paginated(db_session, params=params)
    return IGetResponseBase[Page[IRead]](data=permissions, meta=meta)


@router.get("/permission/{permission_id}", response_model=IGetResponseBase[IRead])
async def get(
    permission_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user()),
):
    permission = await crud.permission.get(db_session, id=permission_id)
    return IGetResponseBase[IRead](data=permission)


@router.post("/permission", response_model=IPostResponseBase[IRead])
async def create(
    new_permission: ICreate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    if await crud.permission.get_permission_by_resource_id_role_id(db_session, permission=new_permission):
        raise AlreadyExistsException
    new_permission = await crud.permission.create(db_session, obj_in=new_permission)
    return IPostResponseBase[IRead](data=new_permission)


@router.patch("/permission/{permission_id}", response_model=IPutResponseBase[IRead])
async def update(
    permission_id: UUID,
    permission: IUpdate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    current_permission = await crud.permission.get(db_session=db_session, id=permission_id)
    if not current_permission:
        raise NotFoundException

    updated_permission = await crud.permission.update(db_session, obj_current=current_permission, obj_new=permission)
    return IPutResponseBase[IRead](data=updated_permission)


@router.delete("/permission/{permission_id}", response_model=IGetResponseBase[IRead])
async def delete(
    permission_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    permission = await crud.permission.get(db_session=db_session, id=permission_id)
    if not permission:
        raise NotFoundException
    permission = await crud.permission.remove(db_session, id=permission_id)
    return IDeleteResponseBase[IRead](
        data=permission
    )
