from dependency_injector import containers, providers

from core.boosters.application.dashboard.list_booster_dashboard_use_case import ListBoosterDashboardUseCase
from core.order.application.use_cases.booster_accept_order_use_case import BoosterAcceptOrderUseCase


class BoosterDashboardUseCases(containers.DeclarativeContainer):
    services = providers.DependenciesContainer()
    bungie = providers.DependenciesContainer()
    clients = providers.DependenciesContainer()
    orders = providers.DependenciesContainer()
    boosters = providers.DependenciesContainer()
    telegram_notifications = providers.DependenciesContainer()

    list_booster_dashboard_uc = providers.Factory(
        ListBoosterDashboardUseCase,
        destiny_bungie_profile_repository=bungie.profiles_repository,
        destiny_character_repository=bungie.characters_repository,
        service_repository=services.service_rep,
        service_configs_repository=services.service_configs_rep,
        order_objective_repository=orders.order_objectives_repository,
        credentials_repository=clients.clients_credentials_repository
    )

    booster_accept_order_uc = providers.Factory(
        BoosterAcceptOrderUseCase,
        order_objective_repository=orders.order_objectives_repository,
        boosters_repository=boosters.repository,
        event_notifications_repository=telegram_notifications.repository
    )
