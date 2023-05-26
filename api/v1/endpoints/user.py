# # Native # #
import json
from uuid import UUID
from typing import Union, Dict, Any, List

# # Installed # #
import sqlalchemy
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import APIRouter, Depends

# # Package # #
from core.settings import Params, Page
from core.utils import ColumnAnnotation, ApiListUtils
from core.logger import logger
from core.exceptions import AlreadyExistsException, NotFoundException, BadRequestException
from app.user.schema import ICreate, IRead, IUpdate, IFilter
from app.user.util import get_current_user
from core.database.session import get_session
from app import crud
from app.model import User
from app.role.model import Role
from app.role.schema import IFilter as RoleFilter
from core.base.schema import (
    IDeleteResponseBase,
    IGetResponseBase,
    IPostResponseBase,
    IPutResponseBase
)

router = APIRouter()

# Если связь many to many то необходимо указывать целевую таблицу и связь из начальной таблицы.
mapping_filters = {
    "roles": {
        "model": [Role, User.roles],
        "filter": RoleFilter
    }
}

utils = ApiListUtils(mapping=mapping_filters, ifilter=IFilter, iread=IRead)

@router.get("/user/list", response_model=IGetResponseBase[Page[IRead]], response_model_exclude_none=True)
async def list(
    params: Params = Depends(),
    db_session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user()),
    filters: dict = Depends(utils.filters),
    scope: set = Depends(utils.scope)
):
    meta = {
        "table_name": "user",
        "table_mapping": [
            ColumnAnnotation(column_name="id", key_name="id"),
            ColumnAnnotation(column_name="обновлено", key_name="updated_at", column_type="datetime"),
            ColumnAnnotation(column_name="создано", key_name="created_at", column_type="datetime"),
            ColumnAnnotation(column_name="обновил", key_name="updated_by"),
            ColumnAnnotation(column_name="создал", key_name="created_by"),
            ColumnAnnotation(column_name="имя", key_name="first_name", default_visibility=True),
            ColumnAnnotation(column_name="фамилия", key_name="last_name", default_visibility=False),
            ColumnAnnotation(column_name="фио", key_name="full_name", default_visibility=True),
            ColumnAnnotation(column_name="почта", key_name="email", default_visibility=True),
            ColumnAnnotation(column_name="активен", key_name="is_active", default_visibility=True),
            ColumnAnnotation(column_name="фото", key_name="picture", column_type="image", default_visibility=True),
        ]
    }
    data = await crud.user.get_multi_paginated(db_session, params=params, filters=filters, scope=scope)
    return IGetResponseBase[Page[IRead]](data=data, meta=meta)


@router.get("/user/{user_id}", response_model=IGetResponseBase[IRead])
async def get(
    user_id: UUID,
    db_session: AsyncSession = Depends(get_session),
):
    user = await crud.user.get(db_session, id=user_id)
    return IGetResponseBase[IRead](data=user)


@router.post("/user", response_model=IPostResponseBase[IRead])
async def create(
    new_user: ICreate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    user = await crud.user.get_by_email(db_session, email=new_user.email)
    if user:
        raise AlreadyExistsException
    # TODO assign default roles to user
    user = await crud.user.create(db_session, obj_in=new_user)
    # TODO send email to user with password
    return IPostResponseBase[IRead](data=user)


@router.patch("/user/{user_id}", response_model=IPutResponseBase[IRead])
async def update(
    user_id: UUID,
    new_user: IUpdate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=False)),
):
    user = await crud.user.get(db_session=db_session, id=user_id)
    if not user:
        raise NotFoundException
    user_updated = await crud.user.update(
        db_session=db_session, obj_current=user, obj_new=new_user
    )
    return IPutResponseBase[IRead](data=user_updated)


@router.patch("/user/{user_id}/role/{role_id}", response_model=IPutResponseBase[IRead])
async def update_user_role(
    role_id: UUID,
    user_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    role = await crud.role.get(db_session, id=role_id)
    await crud.user.update_role(db_session, id=user_id, role=role)
    # TODO remove abundant database call
    user = await crud.user.get(db_session, id=user_id)
    return IPutResponseBase[IRead](data=user)


@router.patch("/user/{user_id}/team/{team_id}", response_model=IPutResponseBase[IRead])
async def update_user_team(
    team_id: UUID,
    user_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    team = await crud.team.get(db_session, id=team_id)
    await crud.user.update_team(db_session, id=user_id, team=team)
    # TODO remove abundant database call
    user = await crud.user.get(db_session, id=user_id)
    return IPutResponseBase[IRead](data=user)


@router.patch("/user/{user_id}/visibility_group/{visibility_group_id}", response_model=IPutResponseBase[IRead])
async def update_user_visibility_group(
    visibility_group_id: UUID,
    user_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    visibility_group = await crud.visibility_group.get(db_session, id=visibility_group_id)
    await crud.user.update_visibility_group(db_session, id=user_id, visibility_group=visibility_group)
    # TODO remove abundant database call
    user = await crud.user.get(db_session, id=user_id)
    return IPutResponseBase[IRead](data=user)


@router.delete("/user/{user_id}", response_model=IDeleteResponseBase[IRead])
async def delete(
    user_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    if current_user.id == user_id:
        raise BadRequestException(detail="You cannot delete yourself")
    try:
        user = await crud.user.remove(db_session, id=user_id)
    except sqlalchemy.exc.IntegrityError as e:
        raise BadRequestException(detail=f"user delete failed: {e}")
    return IDeleteResponseBase[IRead](
        data=user
    )


@router.get("/user", response_model=IGetResponseBase[IRead])
async def get_me(
    user: User = Depends(get_current_user()),
):
    return IGetResponseBase[IRead](data=user)


@router.delete("/user", response_model=IGetResponseBase)
async def delete_me(
    db_session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user()),
):
    try:
        await crud.user.remove(db_session, id=user.id)
    except sqlalchemy.exc.IntegrityError as e:
        raise BadRequestException(detail=f"user delete failed: {e}")
    return IDeleteResponseBase()
