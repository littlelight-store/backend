from dependency_injector import containers, providers

from infrastructure.mq.celery_tasks.celery_events_repository import CeleryEventsRepository


class CeleryEventsRepositoryContainer(containers.DeclarativeContainer):
    repository = providers.Factory(
        CeleryEventsRepository
    )
