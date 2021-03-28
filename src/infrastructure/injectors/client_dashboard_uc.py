from dependency_injector import containers, providers

from core.clients.application.dashboard.list_client_dashboard_use_case import ListClientDashboardUseCase
from core.clients.application.dashboard.save_notification_token import SaveNotificationTokenUseCase
from core.clients.application.dashboard.set_membership_credentials_uc import SetMembershipCredentialsUseCase
from core.order.application.use_cases.client_order_status_dispatcher import OrderStatusDispatcher


class ClientDashboardUcContainer(containers.DeclarativeContainer):
    services = providers.DependenciesContainer()
    bungie = providers.DependenciesContainer()
    clients = providers.DependenciesContainer()
    orders = providers.DependenciesContainer()
    boosters = providers.DependenciesContainer()

    list_client_dashboard_uc = providers.Factory(
        ListClientDashboardUseCase,
        destiny_bungie_profile_repository=bungie.profiles_repository,
        destiny_character_repository=bungie.characters_repository,
        service_repository=services.service_rep,
        service_configs_repository=services.service_configs_rep,
        order_repository=orders.client_orders_repository,
        order_objective_repository=orders.order_objectives_repository,
        client_credentials_repository=clients.clients_credentials_repository,
        boosters_repository=boosters.repository
    )

    set_membership_credentials_uc = providers.Factory(
        SetMembershipCredentialsUseCase,
        client_credentials_repository=clients.clients_credentials_repository
    )

    client_order_status_dispatcher_uc = providers.Factory(
        OrderStatusDispatcher,
        order_objective_repository=orders.order_objectives_repository,
    )

    set_token_notification_token_uc = providers.Factory(
        SaveNotificationTokenUseCase,
        notification_tokens_repository=clients.notification_tokens_repository
    )
