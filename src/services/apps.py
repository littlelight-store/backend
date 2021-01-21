from dependency_injector import providers
from django.apps import AppConfig


class ServicesConfig(AppConfig):
    name = 'services'
    verbose_name = 'Services'

    def ready(self):
        from boosting import container
        from services.repositories import (
            DestinyServiceRepository, DestinyServiceConfigRepository,
            DjangoMainPageServicesRepository,
            DjangoServiceDetailedInfoRepository
        )

        container.services.service_rep.override(providers.Factory(DestinyServiceRepository))
        container.services.service_configs_rep.override(providers.Factory(DestinyServiceConfigRepository))
        container.services.main_page_services_repository.override(providers.Factory(DjangoMainPageServicesRepository))
        container.services.service_detailed_info_repository.override(providers.Factory(DjangoServiceDetailedInfoRepository))

