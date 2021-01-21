import logging

from infrastructure.injectors.application import ApplicationContainer
from .celery_app import app as celery_app
from . import settings

logger = logging.getLogger(__name__)


container = ApplicationContainer()
container.config.from_dict(settings.__dict__)

logger.debug(f'Started application CI container {container}')


__all__ = ['celery_app', 'container']
