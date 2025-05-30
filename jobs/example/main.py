
from core.logger import logger


TASK_NAME = "EXAMPLE"


async def lambda_handler(event, context):
    logger.info(f"Event: {event}")
    logger.info(f"Context: {context}")
    
    # business logic here