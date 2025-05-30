import asyncio
import importlib
import logging
import os
from typing import Callable, Dict, Optional

from airflow.models import Variable


# Logger setup
logger = logging.getLogger(__name__)

# Constants
REQUIRED_ENV_VARS = [
    "YANDEX_SECRET_ID",
    "YANDEX_AUTHORIZED_KEY_ID",
    "YANDEX_PRIVATE_KEY_BASE64",
    "YANDEX_SERVICE_ACCOUNT_ID",
]


def set_environment_variables() -> Dict[str, str]:
    """
    Retrieve Yandex Cloud credentials from Airflow Variables and set them as environment variables.

    Returns:
        Dict[str, str]: A dictionary of the environment variables set.

    Raises:
        ValueError: If any required Airflow Variable is missing or invalid.
    """
    env_vars = {}

    for var_name in REQUIRED_ENV_VARS:
        try:
            value = Variable.get(var_name)
            if not value:
                raise ValueError(f"Airflow Variable '{var_name}' is empty or None")
            env_vars[var_name] = value
            os.environ[var_name] = value
            logger.debug(f"Set environment variable '{var_name}'")
        except Exception as e:
            logger.error(f"Failed to set environment variable '{var_name}': {str(e)}")
            raise ValueError(f"Failed to retrieve Airflow Variable '{var_name}': {str(e)}")

    return env_vars


def configure_core_modules() -> None:
    """
    Configure core modules (logger and sentry) to use the wrapper's logger and disable sentry.
    """
    import integration.sentry

    import core.logger

    integration.sentry.sentry_init = lambda: None  # Disable Sentry initialization
    core.logger.logger = logger  # Override core logger with wrapper's logger


def load_lambda_handler(handler_path: str) -> Callable:
    """
    Dynamically load a lambda handler function from a given module path.

    Args:
        handler_path (str): Full path to the handler (e.g., 'jobs.actions_ozon_list.main.lambda_handler').

    Returns:
        Callable: The loaded lambda handler function.

    Raises:
        ImportError: If the module or function cannot be imported.
        AttributeError: If the function name is invalid.
    """
    try:
        module_path, function_name = handler_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, function_name)
    except (ImportError, AttributeError) as e:
        logger.error(f"Failed to load lambda handler '{handler_path}': {str(e)}")
        raise


def job_wrapper(lambda_handler_path: str, event: Optional[Dict] = None, context: Optional[Dict] = None) -> Callable:
    """
    Wrap a lambda handler function with environment setup and execution logging.

    Args:
        lambda_handler_path (str): Path to the lambda handler (e.g., 'jobs.actions_ozon_list.main.lambda_handler').
        event (Optional[Dict]): Event data to pass to the handler. Defaults to empty dict.
        context (Optional[Dict]): Context data to pass to the handler. Defaults to empty dict.

    Returns:
        Callable: A wrapper function that executes the lambda handler.
    """
    set_environment_variables()
    lambda_handler = load_lambda_handler(lambda_handler_path)
    event = event or {}
    context = context or {}

    def wrapper(*args, **kwargs) -> None:

        configure_core_modules()

        if kwargs:
            context.update(kwargs)

        logger.info(f"Executing lambda handler '{lambda_handler_path}' with event: {event}")
        asyncio.run(lambda_handler(event, context))
        logger.info(f"Lambda handler '{lambda_handler_path}' executed successfully")

    return wrapper
