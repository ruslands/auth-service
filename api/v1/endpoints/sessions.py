# # Native # #
from uuid import UUID

# # Installed # #
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends

# # Package # #
from core.settings import Params, Page
from core.exceptions import NotFoundException
from core.utils import ColumnAnnotation, ApiListUtils
from app import crud
from app.model import User
from app.sessions.schema import IRead, IFilter
from app.user.util import get_current_user
from core.database.session import get_session
from core.base.schema import IGetResponseBase, IDeleteResponseBase


router = APIRouter()

utils = ApiListUtils(IFilter, IRead)

@router.get("/sessions/list", response_model=IGetResponseBase[Page[IRead]], response_model_exclude_none=True)
async def read_sessions_list(
    params: Params = Depends(),
    db_session: AsyncSession = Depends(get_session),
    # current_user: User = Depends(get_current_user()),
    filters: dict = Depends(utils.filters),
    scope: set = Depends(utils.scope)
):
    """
    Retrieve sessions.
    """
    sessions = await crud.sessions.get_multi_paginated(db_session, params=params)
    return IGetResponseBase[Page[IRead]](data=sessions)


@router.delete("/sessions/{session_id}", response_model=IDeleteResponseBase[IRead])
async def remove_session(
    session_id: UUID,
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),

):
    current_session = await crud.sessions.get(db_session=db_session, id=session_id)
    if not current_session:
        raise NotFoundException
    session = await crud.sessions.remove(db_session, id=session_id)
    return IDeleteResponseBase[IRead](data=session)
