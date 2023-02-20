# # Native # #
from typing import Optional
from urllib.parse import urlparse

# # Installed # #
from pydantic import BaseModel, validator

# # Installed # #
from core.logger import logger

__all__ = (
    "IRBACRead",
    "IRBACValidate",
    "IRBACValidateResponse",
)


class IRBACRead(BaseModel):
    roles: Optional[dict]
    teams: Optional[dict]
    resources: Optional[dict]
    permissions: Optional[dict]


class IRBACValidate(BaseModel):
    method: str
    endpoint: str

    @validator('method')
    def method_must_be_lower(cls, v):
        if v.lower().strip() not in ['get', 'post', 'put', 'delete', 'patch']:
            logger.info(f"Invalid permission method [{v}], aborted!!")
            raise ValueError(f"Invalid permission method [{v}]")
        return v.lower().strip()

    @validator('endpoint')
    def normalizing_endpoint(cls, v):
        logger.debug(f"endpoint before normalizing: {v}")
        v = urlparse(v).path.lower().strip()
        for prefix in ['/local', '/dev', '/production', '/staging', '/development']:
            if v.startswith(prefix):
                v = v.replace(prefix, '')
                break
        logger.debug(f"endpoint after normalizing: {v}")
        if not v.startswith('/'):
            logger.info(f"Invalid permission path [{v}], aborted!!")
            raise ValueError(f"Invalid permission path [{v}]")
        return v


class IRBACValidateResponse(BaseModel):
    access: bool = True
    rbac_enable: bool = False
    visibility_group_enable: bool = False
    # permissions: list = []
    detail: str = ""
