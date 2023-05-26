# # Installed # #
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordBearer

# # Package # #
from core.settings import settings
from core.database.session import get_session
from app.rbac.schema import IRBACRead
from app.rbac.schema import IRBACValidateResponse, IRBACValidate
from core.base.schema import IGetResponseBase

router = APIRouter()

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.HOSTNAME}/api/auth/access-token"
)


@router.get("/rbac", response_model=IGetResponseBase[IRBACRead])
async def get_rbac_rules(
    request: Request,
    db_session: AsyncSession = Depends(get_session),
):
    data = await request.app.rbac.get(db_session)
    return IGetResponseBase[IRBACRead](data=data)


@router.post("/rbac/validate", response_model=IGetResponseBase[IRBACValidateResponse])
async def validate(
    request: Request,
    req: IRBACValidate,
    access_token: str = Depends(reusable_oauth2),
    db_session: AsyncSession = Depends(get_session),
):
    data = await request.app.rbac.validate(db_session=db_session, req=req, access_token=access_token)
    return IGetResponseBase[IRBACValidateResponse](data=data)
