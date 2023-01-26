# # Native # #

# # Installed # #
import sentry_sdk
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# # Package # #


class UserMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request.scope["user_email"] = (
            request.scope.get("aws.event", {})
            .get("requestContext", {})
            .get("authorizer", {})
            .get("email")
        )
        if request.scope["user_email"]:
            sentry_sdk.set_user({"email": request.scope["user_email"]})
        return await call_next(request)
