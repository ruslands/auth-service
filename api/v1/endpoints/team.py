# # Native # #
from uuid import UUID

# # Installed # #
import sqlalchemy
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends

# # Package # #
from core.settings import Params, Page
from core.exceptions import NotFoundException, AlreadyExistsException, BadRequestException
from app.model import User
from core.base.schema import (
    IDeleteResponseBase,
    IGetResponseBase,
    IPostResponseBase,
    IPutResponseBase,
)
from app.team.schema import ICreate, IRead, IFilter, IUpdate
from app import crud
from app.user.util import get_current_user
from core.database.session import get_session
from core.utils import ColumnAnnotation, ApiListUtils

router = APIRouter()

utils = ApiListUtils(IFilter, IRead)

@router.get("/team/list", response_model=IGetResponseBase[Page[IRead]], response_model_exclude_none=True)
async def list(
    params: Params = Depends(),
    db_session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user()),
    filters: dict = Depends(utils.filters),
    scope: set = Depends(utils.scope)
):
    meta = {
        "table_name": "team",
        "table_mapping": [
            ColumnAnnotation(column_name="id", key_name="id"),
            ColumnAnnotation(column_name="обновлено", key_name="updated_at", column_type="datetime"),
            ColumnAnnotation(column_name="создано", key_name="created_at", column_type="datetime"),
            ColumnAnnotation(column_name="обновил", key_name="updated_by"),
            ColumnAnnotation(column_name="создал", key_name="created_by"),
            ColumnAnnotation(column_name="группа", key_name="name", default_visibility=True)
        ]
    }
    teams = await crud.team.get_multi_paginated(db_session, params=params)
    return IGetResponseBase[Page[IRead]](data=teams, meta=meta)


@router.get("/team/{team_id}", response_model=IGetResponseBase[IRead])
async def get(
    team_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user()),
):
    team = await crud.team.get(db_session, id=team_id)
    if not team:
        raise NotFoundException
    return IGetResponseBase[IRead](data=team)


@router.post("/team", response_model=IPostResponseBase[IRead])
async def create(
    team: ICreate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    try:
        team = await crud.team.create(db_session, obj_in=team, created_by=current_user.id)
    except sqlalchemy.exc.IntegrityError as e:
        if "UniqueViolationError" in str(e):
            raise AlreadyExistsException
        raise BadRequestException(detail=f"Team creation failed: {e}")
    return IPostResponseBase[IRead](data=team)


@router.patch("/team/{team_id}", response_model=IPostResponseBase[IRead])
async def update(
    team_id: UUID,
    team: IUpdate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    current_team = await crud.team.get(db_session=db_session, id=team_id)
    if not current_team:
        raise NotFoundException
    team.updated_by = current_user.id
    try:
        team_updated = await crud.team.update(
            db_session=db_session,
            obj_current=current_team,
            obj_new=team
        )
    except sqlalchemy.exc.IntegrityError as e:
        raise BadRequestException(detail=f"Team update failed: {e}")
    return IPutResponseBase[IRead](data=team_updated)


@router.delete("/team/{team_id}", response_model=IDeleteResponseBase[IRead])
async def delete(
    team_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),

):
    current_team = await crud.team.get(db_session=db_session, id=team_id)
    if not current_team:
        raise NotFoundException
    team = await crud.team.remove(db_session, id=team_id)
    return IDeleteResponseBase[IRead](data=team)
