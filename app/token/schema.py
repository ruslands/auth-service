# # Native # #
from typing import Optional

# # Installed # #
from pydantic import BaseModel

# # Package # #


class Token(BaseModel):
    access_token: str
    expires_at: int  # Unix timestamp in seconds
    token_type: str
    refresh_token: Optional[str]


class RefreshToken(BaseModel):
    refresh_token: str
