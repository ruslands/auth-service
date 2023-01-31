# # Native # #
from uuid import UUID

# # Installed # #
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends

# # Package # #
from app.utils.settings import Params, Page
from app.utils.exceptions import NotFoundException
from app import crud
from app.models import User
from app.schemas.sessions import IRead
from app.database.user import get_current_user
from app.database.session import get_session
from app.schemas.common import IGetResponseBase, IDeleteResponseBase


router = APIRouter()


@router.get("/sessions/list", response_model=IGetResponseBase[Page[IRead]])
async def read_sessions_list(
    params: Params = Depends(),
    db_session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user(required_permissions=True)),
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
