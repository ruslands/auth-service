import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from sentry_sdk.integrations.logging import BreadcrumbHandler, EventHandler

from core.logger import logger
from core.settings import settings


__all__ = "sentry_init"

logger.add(BreadcrumbHandler(level="INFO"), level="INFO")
logger.add(EventHandler(level="ERROR"), level="ERROR")

integrations = [
    AwsLambdaIntegration(timeout_warning=True),
]


def sentry_init():
    if settings.SENTRY_ENABLED:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            integrations=integrations,
            debug=False,
            # debug=settings.DEBUG,
            attach_stacktrace=True,
            request_bodies="always",
            # Set traces_sample_rate to 1.0 to capture 100% If set to 0.1 only 10% of error events will be sent. Events are picked randomly. # noqa
            traces_sample_rate=0.2,
            max_breadcrumbs=100,
        )
