from dependency_injector import containers, providers

from core.boosters.application.repository import BoostersRepository


class BoostersContainer(containers.DeclarativeContainer):
    repository = providers.ExternalDependency(BoostersRepository)
