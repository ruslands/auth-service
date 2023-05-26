# # Native # #
from uuid import UUID

# # Installed # #
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends

# # Package # #
from core.settings import Params, Page
from core.exceptions import AlreadyExistsException, NotFoundException
from core.utils import ColumnAnnotation, ApiListUtils
from app import crud
from app.user.util import get_current_user
from core.database.session import get_session
from app.model import User
from app.resource.schema import ICreate, IRead, IUpdate, IFilter
from core.base.schema import IGetResponseBase, IPostResponseBase, IPutResponseBase, IDeleteResponseBase

router = APIRouter()

utils = ApiListUtils(IFilter, IRead)

@router.get("/resource/list", response_model=IGetResponseBase[Page[IRead]], response_model_exclude_none=True)
async def list(
    params: Params = Depends(),
    db_session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user()),
    filters: dict = Depends(utils.filters),
    scope: set = Depends(utils.scope)
):
    resources = await crud.resource.get_multi_paginated(db_session, params=params)
    return IGetResponseBase[Page[IRead]](data=resources)


@router.get("/resource/{resource_id}", response_model=IGetResponseBase[IRead])
async def get(
    resource_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=False)),
):
    resource = await crud.resource.get(db_session, id=resource_id)
    return IGetResponseBase[IRead](data=resource)


@router.post("/resource", response_model=IPostResponseBase[IRead])
async def create(
    resource: ICreate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=False)),
):
    if await crud.resource.get_resource_by_endpoint_and_method(db_session, endpoint=resource.endpoint, method=resource.method):
        raise AlreadyExistsException
    # new_resource = await crud.resource.create(db_session, obj_in=resource, created_by_id=current_user.id)
    new_resource = await crud.resource.create(db_session, obj_in=resource)
    return IPostResponseBase[IRead](data=new_resource)


@router.patch("/resource/{resource_id}", response_model=IPutResponseBase[IRead])
async def update(
    resource_id: UUID,
    resource: IUpdate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=False)),
):
    resource_current = await crud.resource.get(db_session=db_session, id=resource_id)
    if not resource_current:
        raise NotFoundException

    resource_updated = await crud.resource.update(db_session, obj_current=resource_current, obj_new=resource)
    return IPutResponseBase[IRead](data=resource_updated)


@router.delete("/resource/{resource_id}", response_model=IDeleteResponseBase[IRead])
async def delete(
    resource_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=False)),

):
    resource_current = await crud.resource.get(db_session=db_session, id=resource_id)
    if not resource_current:
        raise NotFoundException
    resource = await crud.resource.remove(db_session, id=resource_id)
    return IDeleteResponseBase[IRead](data=resource)
