# # Native # #
from uuid import UUID

# # Installed # #
import sqlalchemy
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends

# # Package # #
from app.utils.settings import Params, Page
from app.utils.exceptions import NotFoundException, AlreadyExistsException, BadRequestException
from app.models.user import User
from app.schemas.common import (
    IDeleteResponseBase,
    IGetResponseBase,
    IPostResponseBase,
    IPutResponseBase,
)
from app.schemas.team import ITeamCreate, ITeamRead, ITeamReadWithUsers, ITeamUpdate
from app import crud
from app.database.user import get_current_user
from app.database.session import get_session

router = APIRouter()


@router.get("/team/list", response_model=IGetResponseBase[Page[ITeamRead]])
async def get_teams_list(
    params: Params = Depends(),
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user()),
):
    teams = await crud.team.get_multi_paginated(db_session, params=params)
    return IGetResponseBase[Page[ITeamRead]](data=teams)


@router.get("/team/{team_id}", response_model=IGetResponseBase[ITeamReadWithUsers])
async def get_team_by_id(
    team_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user()),
):
    team = await crud.team.get(db_session, id=team_id)
    if not team:
        raise NotFoundException
    return IGetResponseBase[ITeamReadWithUsers](data=team)


@router.post("/team", response_model=IPostResponseBase[ITeamRead])
async def create_team(
    team: ITeamCreate,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
):
    if await crud.team.get_team_by_name(db_session, name=team.name):
        raise AlreadyExistsException
    team = await crud.team.create(db_session, obj_in=team, created_by=current_user.id)
    return IPostResponseBase[ITeamRead](data=team)


@router.patch("/team/{team_id}", response_model=IPostResponseBase[ITeamRead])
async def update_team(
    team_id: UUID,
    team: ITeamUpdate,
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
    return IPutResponseBase[ITeamRead](data=team_updated)


@router.delete("/team/{team_id}", response_model=IDeleteResponseBase[ITeamRead])
async def remove_team(
    team_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),

):
    current_team = await crud.team.get(db_session=db_session, id=team_id)
    if not current_team:
        raise NotFoundException
    team = await crud.team.remove(db_session, id=team_id)
    return IDeleteResponseBase[ITeamRead](data=team)
