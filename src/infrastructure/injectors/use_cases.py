from dependency_injector import containers, providers

from core.application.use_cases.list_main_page_goods import ListMainPageGoodsUseCase
from core.application.use_cases.service_page import ServicePageUseCase


class UseCases(containers.DeclarativeContainer):
    services = providers.DependenciesContainer()

    list_main_page_goods_uc = providers.Factory(
        ListMainPageGoodsUseCase,
        main_page_services_repository=services.main_page_services_repository
    )

    get_service_detailed_info_uc = providers.Factory(
        ServicePageUseCase,
        service_detailed_info_repository=services.service_detailed_info_repository,
        service_configs_rep=services.service_configs_rep
    )
