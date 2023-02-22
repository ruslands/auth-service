# # Native # #
import os
import asyncio
# import uvloop
# uvloop.install()

# # Installed # #
from mangum import Mangum
from sqladmin import Admin  # noqa
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# # Package # #
from app.rbac.util import RBAC
from app.visibility_group.util import VisibilityGroup
from core.database.admin import UserAdmin, RoleAdmin, SessionsAdmin, TeamAdmin, ResourceAdmin, VisibilityGroupAdmin  # noqa
from core.database.database import async_engine, init_database
from api.v1.api import router
from core.settings import settings
from core.logger import logger
from core.sentry import sentry_init
from core.middleware import UserMiddleware

sentry_init()


app = FastAPI(
    title=settings.PROJECT_NAME, 
    description='auth service',
    version='1.0.0',
    openapi_url="/auth/openapi.json",
    openapi_tags=[{
        'name': 'auth',
        'description': 'authentication and authorisation',
    }],
    docs_url="/auth/docs", 
    redoc_url="/auth/redoc"
)

app.include_router(router)

app.rbac = RBAC()  # store role based access control settings in the app context
app.visibility_group = VisibilityGroup()  # store visibility groups settings in the app context

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # remove this in production
    allow_methods=["*"], # remove this in production
    allow_headers=["*"], # remove this in production
)
app.add_middleware(UserMiddleware)

lambda_handler = None


async def init_admin():
    admin = Admin(app, async_engine, base_url='/auth/admin')
    models = [UserAdmin, RoleAdmin, SessionsAdmin,
              TeamAdmin, ResourceAdmin, VisibilityGroupAdmin]

    for model in models:
        admin.register_model(model)


async def on_startup():
    await asyncio.gather(init_database(), init_admin())
# await asyncio.gather(init_admin())


def wrapper(event, context):
    logger.debug(f"event: {event}")
    results = lambda_handler(event, context)
    logger.debug(f"results: {results}")
    return results


if os.getenv("AWS_LAMBDA_RUNTIME_API"):
    # mangum emits "startup" event on each request, therefore make it init only once
    logger.debug("Running on AWS Lambda")
    # app.on_event("startup")(on_startup)
    lambda_handler = Mangum(app, lifespan="on", api_gateway_base_path=app.root_path)
    # logger.add(lambda_handler, enqueue=False)
else:
    app.on_event("startup")(on_startup)
    ...
