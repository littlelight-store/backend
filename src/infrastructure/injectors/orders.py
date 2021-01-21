from dependency_injector import containers, providers

from core.order.application.repository import ClientOrderRepository, OrderObjectiveRepository
from core.order.application.use_cases.order_created_notifications import OrderCreatedNotificationsUseCase
from core.order.application.use_cases.process_payment_callback_uc import ProcessPaymentCallbackUseCase


class OrdersUseCases(containers.DeclarativeContainer):

    email_notificator = providers.Dependency()
    telegram_notifications = providers.DependenciesContainer()
    services = providers.DependenciesContainer()
    clients = providers.DependenciesContainer()
    bungie = providers.DependenciesContainer()
    orders = providers.DependenciesContainer()

    order_created_notifications_uc = providers.Factory(
        OrderCreatedNotificationsUseCase,
        event_notifications_repository=telegram_notifications.repository,
        client_orders_repository=orders.client_orders_repository,
        order_objectives_repository=orders.order_objectives_repository,
        services_repository=services.service_rep,
        service_configs_repository=services.service_configs_rep,
        destiny_bungie_profile_repository=bungie.profiles_repository,
        destiny_character_repository=bungie.characters_repository,
        clients_repository=clients.clients_repository,
        email_notificator=email_notificator
    )

    process_payment_callback_uc = providers.Factory(
        ProcessPaymentCallbackUseCase,
        client_orders_repository=orders.client_orders_repository,
        order_objectives_repository=orders.order_objectives_repository,
    )


class OrdersContainer(containers.DeclarativeContainer):
    client_orders_repository = providers.ExternalDependency(ClientOrderRepository)
    order_objectives_repository = providers.ExternalDependency(OrderObjectiveRepository)
