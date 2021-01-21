from dependency_injector import containers, providers

from core.application.repositories.aggregates.main_page_services_repository import MainPageServicesRepository
from core.application.repositories.services import (
    ServiceConfigsRepository, ServiceDetailedInfoRepository,
    ServiceRepository,
)
from core.shopping_cart.application.repository import PromoCodeRepository


class DestinyServiceContainer(containers.DeclarativeContainer):
    service_rep = providers.ExternalDependency(ServiceRepository)
    service_configs_rep = providers.ExternalDependency(ServiceConfigsRepository)

    promo_code_repository = providers.ExternalDependency(PromoCodeRepository)

    main_page_services_repository = providers.ExternalDependency(MainPageServicesRepository)
    service_detailed_info_repository = providers.ExternalDependency(ServiceDetailedInfoRepository)
