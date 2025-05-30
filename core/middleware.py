import sentry_sdk

# from pyinstrument import Profiler
# from pyinstrument.renderers.html import HTMLRenderer
# from pyinstrument.renderers.speedscope import SpeedscopeRenderer
from sqlalchemy.exc import IntegrityError
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

from core.exceptions import BadRequestException, BaseAPIException
from core.settings import settings


class UserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if settings.SENTRY_ENABLED:
            user_email = request.scope.get("aws.event", {}).get("requestContext", {}).get("authorizer", {}).get("email")
            if user_email:
                sentry_sdk.set_user({"email": user_email})
        return await call_next(request)


class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.scope["context"] = request.scope.get("aws.event", {}).get("requestContext", {}).get("authorizer", {})
        return await call_next(request)


class CustomHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        if response.status_code == 303:
            response.headers["X-UI-TOAST"] = "false"
        elif response.status_code == 422:
            response.headers["X-UI-TOAST"] = "true"
        return response


class CustomExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except IntegrityError as e:
            match request.method:
                case "POST":
                    action = "create"
                case "PATCH" | "PUT":
                    action = "update"
                case "DELETE":
                    action = "delete"
                case "GET":
                    action = "get"
                case _:
                    action = "action"
            raise BadRequestException(detail=f"Entity {action} failed: {e}")
        except BaseAPIException:
            raise
        except Exception as exc:
            raise BadRequestException(detail=str(exc))


# class ProfileMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         """Profile the current request
#
#         Taken from https://pyinstrument.readthedocs.io/en/latest/guide.html#profile-a-web-request-in-fastapi
#         with small improvements.
#
#         """
#         # we map a profile type to a file extension, as well as a pyinstrument profile renderer
#         profile_type_to_ext = {"html": "html", "speedscope": "speedscope.json"}
#         profile_type_to_renderer = {
#             "html": HTMLRenderer,
#             "speedscope": SpeedscopeRenderer,
#         }
#
#         # if the `profile=true` HTTP query argument is passed, we profile the request
#         if True:  # request.query_params.get("profile", False):
#             # The default profile format is speedscope
#             profile_type = request.query_params.get("profile_format", "html")
#
#             # we profile the request along with all additional middlewares, by interrupting
#             # the program every 1ms1 and records the entire stack at that point
#             with Profiler(interval=0.001, async_mode="enabled") as profiler:
#                 response = await call_next(request)
#
#             # we dump the profiling into a file
#             extension = profile_type_to_ext[profile_type]
#             renderer = profile_type_to_renderer[profile_type]()
#             with open(f"profile.{extension}", "w") as out:
#                 out.write(profiler.output(renderer=renderer))
#             return response
#
#         # Proceed without profiling
#         return await call_next(request)
