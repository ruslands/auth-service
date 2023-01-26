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
from app.schemas.resource import IResourceCreate, IResourceRead, IResourceUpdate
from app.schemas.common import IGetResponseBase, IPostResponseBase, IPutResponseBase, IDeleteResponseBase

router = APIRouter()


@router.get("/resource/list", response_model=IGetResponseBase[Page[IResourceRead]])
async def get_resources(
    params: Params = Depends(),
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=False)),
):
    resources = await crud.resource.get_multi_paginated(db_session, params=params)
    return IGetResponseBase[Page[IResourceRead]](data=resources)


@router.get("/resource/{resource_id}", response_model=IGetResponseBase[IResourceRead])
async def get_resource_by_id(
    resource_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=False)),
):
    resource = await crud.resource.get(db_session, id=resource_id)
    return IGetResponseBase[IResourceRead](data=resource)


@router.post("/resource", response_model=IPostResponseBase[IResourceRead])
async def create_resource(
    resource: IResourceCreate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=False)),
):
    if await crud.resource.get_resource_by_endpoint_and_method(db_session, endpoint=resource.endpoint, method=resource.method):
        raise AlreadyExistsException
    # new_resource = await crud.resource.create(db_session, obj_in=resource, created_by_id=current_user.id)
    new_resource = await crud.resource.create(db_session, obj_in=resource)
    return IPostResponseBase[IResourceRead](data=new_resource)


@router.patch("/resource/{resource_id}", response_model=IPutResponseBase[IResourceRead])
async def update_resource(
    resource_id: UUID,
    resource: IResourceUpdate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=False)),
):
    resource_current = await crud.resource.get(db_session=db_session, id=resource_id)
    if not resource_current:
        raise NotFoundException

    resource_updated = await crud.resource.update(db_session, obj_current=resource_current, obj_new=resource)
    return IPutResponseBase[IResourceRead](data=resource_updated)


@router.delete("/resource/{resource_id}", response_model=IDeleteResponseBase[IResourceRead])
async def remove_team(
    resource_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=False)),

):
    resource_current = await crud.resource.get(db_session=db_session, id=resource_id)
    if not resource_current:
        raise NotFoundException
    resource = await crud.resource.remove(db_session, id=resource_id)
    return IDeleteResponseBase[IResourceRead](data=resource)
