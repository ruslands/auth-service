# # Native # #

# # Installed # #
import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from sentry_sdk.integrations.logging import (
    BreadcrumbHandler,
    EventHandler,
)

# # Package # #
from core.settings import settings
from core.logger import logger

__all__ = (
    "sentry_init"
)

logger.add(BreadcrumbHandler(level="INFO"), level="INFO")
logger.add(EventHandler(level="ERROR"), level="ERROR")

integrations = [
    AwsLambdaIntegration(timeout_warning=True),
]


def sentry_init():
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=integrations,
        debug=settings.DEBUG,
        attach_stacktrace=True,
        request_bodies='always',
        # Set traces_sample_rate to 1.0 to capture 100% If set to 0.1 only 10% of error events will be sent. Events are picked randomly. # noqa
        traces_sample_rate=0.2,
        max_breadcrumbs=100
    )
