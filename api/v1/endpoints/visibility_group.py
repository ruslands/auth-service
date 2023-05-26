# # Native # #
from uuid import UUID

# # Installed # #
import sqlalchemy
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordBearer

# # Package # #
from core.security import verify_jwt_token
from core.settings import Params, Page, settings
from core.exceptions import NotFoundException, AlreadyExistsException, BadRequestException
from app.model import User
from core.base.schema import IDeleteResponseBase, IGetResponseBase, IPostResponseBase, IPutResponseBase
from app.visibility_group.schema import ICreate, IRead, IUpdate, IFilter, IVisibilityGroupValidateResponse
from app import crud
from app.user.util import get_current_user
from core.database.session import get_session
from core.logger import logger
from core.constants import VISIBILITY_GROUP_ENTITY_POSSIBLE_VALUES
from core.utils import ColumnAnnotation, ApiListUtils

router = APIRouter()

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.HOSTNAME}/api/auth/access-token"
)

utils = ApiListUtils(IFilter, IRead)

@router.get("/visibility_group/list", response_model=IGetResponseBase[Page[IRead]], response_model_exclude_none=True)
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
            ColumnAnnotation(column_name="префикс", key_name="prefix", default_visibility=True),
            ColumnAnnotation(column_name="админ", key_name="admin", default_visibility=False),
            ColumnAnnotation(column_name="???", key_name="opportunity", default_visibility=True),
            ColumnAnnotation(column_name="продавец", key_name="seller", default_visibility=True),
            ColumnAnnotation(column_name="активность", key_name="activity", default_visibility=True),
            ColumnAnnotation(column_name="свойства", key_name="property", default_visibility=True)
        ]
    }
    visibility_groups = await crud.visibility_group.get_multi_paginated(db_session, params=params)
    return IGetResponseBase[Page[IRead]](data=visibility_groups, meta=meta)


# TODO: add response model
@router.get("/visibility_group/settings")
async def get_visibility_group_settings(
    request: Request,
    db_session: AsyncSession = Depends(get_session),
):
    data = await request.app.visibility_group.get(db_session)
    logger.debug(f"get_visibility_group_settings: {data}")
    return data


@router.get("/visibility_group/validate/{visibility_group_entity}", response_model=IGetResponseBase[IVisibilityGroupValidateResponse])
async def validate(
    request: Request,
    visibility_group_entity: str,
    access_token: str = Depends(reusable_oauth2),
    db_session: AsyncSession = Depends(get_session),
):

    visibility_group_entity = visibility_group_entity.lower().strip()
    if visibility_group_entity not in VISIBILITY_GROUP_ENTITY_POSSIBLE_VALUES:
        raise BadRequestException(
            detail=f'Invalid value: {visibility_group_entity}. Possible values: {VISIBILITY_GROUP_ENTITY_POSSIBLE_VALUES}')

    data = await request.app.visibility_group.validate(
        db_session=db_session,
        visibility_group_entity=visibility_group_entity,
        access_token=access_token
    )

    meta = await verify_jwt_token(token=access_token, token_type="access", db_session=db_session, crud=crud)

    return IGetResponseBase[IVisibilityGroupValidateResponse](meta=meta, data=data)


@router.get("/visibility_group/{visibility_group_id}", response_model=IGetResponseBase[IRead])
async def get(
    visibility_group_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user()),
):
    visibility_group = await crud.visibility_group.get(db_session, id=visibility_group_id)
    if not visibility_group:
        raise NotFoundException
    return IGetResponseBase[IRead](data=visibility_group)


@router.post("/visibility_group", response_model=IPostResponseBase[IRead])
async def create(
    visibility_group: ICreate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    if await crud.visibility_group.get_visibility_group_by_prefix(db_session, prefix=visibility_group.prefix):
        raise AlreadyExistsException
    visibility_group = await crud.visibility_group.create(db_session, obj_in=visibility_group, created_by=current_user.id)
    return IPostResponseBase[IRead](data=visibility_group)


@router.patch("/visibility_group/{visibility_group_id}", response_model=IPostResponseBase[IRead])
async def update(
    visibility_group_id: UUID,
    visibility_group: IUpdate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    current_visibility_group = await crud.visibility_group.get(db_session=db_session, id=visibility_group_id)
    if not current_visibility_group:
        raise NotFoundException
    visibility_group.updated_by = current_user.id
    try:
        visibility_group_updated = await crud.visibility_group.update(
            db_session=db_session,
            obj_current=current_visibility_group,
            obj_new=visibility_group
        )
    except sqlalchemy.exc.IntegrityError as e:
        raise BadRequestException(detail=f"Visibility group update failed: {e}")
    return IPutResponseBase[IRead](data=visibility_group_updated)


@router.delete("/visibility_group/{visibility_group_id}", response_model=IDeleteResponseBase[IRead])
async def delete(
    visibility_group_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),

):
    current_visibility_group = await crud.visibility_group.get(db_session=db_session, id=visibility_group_id)
    if not current_visibility_group:
        raise NotFoundException
    visibility_group = await crud.visibility_group.remove(db_session, id=visibility_group_id)
    return IDeleteResponseBase[IRead](data=visibility_group)
