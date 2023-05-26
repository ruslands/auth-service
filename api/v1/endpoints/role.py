# # Native # #
from uuid import UUID

# # Installed # #
import sqlalchemy
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends

# # Package # #
from core.settings import Params, Page
from core.logger import logger
from core.exceptions import AlreadyExistsException, NotFoundException, BadRequestException
from app import crud
from app.user.util import get_current_user
from core.database.session import get_session
from app.model import User
from app.role.schema import ICreate, IRead, IUpdate, IFilter
from core.base.schema import (
    IGetResponseBase,
    IPostResponseBase,
    IPutResponseBase,
    IDeleteResponseBase
)
from core.utils import ColumnAnnotation, ApiListUtils

router = APIRouter()

utils = ApiListUtils(IFilter, IRead)

@router.get("/role/list", response_model=IGetResponseBase[Page[IRead]], response_model_exclude_none=True)
async def list(
    params: Params = Depends(),
    db_session: AsyncSession = Depends(get_session),
    filters: dict = Depends(utils.filters),
    scope: set = Depends(utils.scope)
    # current_user: User = Depends(get_current_user()),
):
    meta = {
        "table_name": "role",
        "table_mapping": [
            ColumnAnnotation(column_name="id", key_name="id"),
            ColumnAnnotation(column_name="обновлено", key_name="updated_at", column_type="datetime"),
            ColumnAnnotation(column_name="создано", key_name="created_at", column_type="datetime"),
            ColumnAnnotation(column_name="обновил", key_name="updated_by"),
            ColumnAnnotation(column_name="создал", key_name="created_by"),
            ColumnAnnotation(column_name="роль", key_name="name", default_visibility=True)
        ]
    }
    roles = await crud.role.get_multi_paginated(db_session, params=params, filters=filters, scope=scope)
    return IGetResponseBase[Page[IRead]](data=roles, meta=meta)


@router.get("/role/{role_id}", response_model=IGetResponseBase[IRead])
async def get(
    role_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user()),
):
    role = await crud.role.get(db_session, id=role_id)
    logger.debug(role)
    return IGetResponseBase[IRead](data=role)


@router.post("/role", response_model=IPostResponseBase[IRead])
async def create(
    role: ICreate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    try:
        role = await crud.role.create(db_session, obj_in=role)
    except sqlalchemy.exc.IntegrityError as e:
        if "UniqueViolationError" in str(e):
            raise AlreadyExistsException
        raise BadRequestException(detail=f"Role creation failed: {e}")
    return IPostResponseBase[IRead](data=role)


@router.patch("/role/{role_id}", response_model=IPutResponseBase[IRead])
async def update(
    role_id: UUID,
    role: IUpdate,
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
    return IPutResponseBase[IRead](data=updated_role)


@router.delete("/role/{role_id}", response_model=IGetResponseBase[IRead])
async def delete(
    role_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    role = await crud.role.get(db_session=db_session, id=role_id)
    if not role:
        raise NotFoundException
    role = await crud.role.remove(db_session, id=role_id)
    return IDeleteResponseBase[IRead](
        data=role
    )
