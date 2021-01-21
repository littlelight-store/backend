from dependency_injector import containers, providers

from services.repositories import DestinyServiceConfigRepository, DestinyServiceRepository, DestinyServiceTagRepository


class DestinyServiceInjectors(containers.DeclarativeContainer):
    service_tag_rep = providers.Factory(DestinyServiceTagRepository)
    service_rep = providers.Factory(DestinyServiceRepository)
    service_configs_rep = providers.Factory(DestinyServiceConfigRepository)
