from dependency_injector import containers, providers

from core.boosters.application.dashboard.list_booster_dashboard_use_case import ListBoosterDashboardUseCase


class BoosterDashboardUseCases(containers.DeclarativeContainer):
    services = providers.DependenciesContainer()
    bungie = providers.DependenciesContainer()
    clients = providers.DependenciesContainer()
    orders = providers.DependenciesContainer()

    list_booster_dashboard_uc = providers.Factory(
        ListBoosterDashboardUseCase,
        destiny_bungie_profile_repository=bungie.profiles_repository,
        destiny_character_repository=bungie.characters_repository,
        service_repository=services.service_rep,
        service_configs_repository=services.service_configs_rep,
        order_objective_repository=orders.order_objectives_repository,
        credentials_repository=clients.clients_credentials_repository
    )
