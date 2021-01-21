from dependency_injector import containers, providers

from infrastructure.injectors.boosters import BoostersContainer
from infrastructure.injectors.bungie import BungieContainer
from infrastructure.injectors.celery import CeleryEventsRepositoryContainer
from infrastructure.injectors.client_dashboard_uc import ClientDashboardUcContainer
from infrastructure.injectors.clients import ClientsContainer
from infrastructure.injectors.notificators import TelegramNotificationsContainer
from infrastructure.injectors.orders import OrdersContainer, OrdersUseCases
from infrastructure.injectors.services import DestinyServiceContainer
from infrastructure.injectors.shopping_cart import ShoppingCartContainer, ShoppingCartUseCases
from infrastructure.injectors.use_cases import UseCases
from notificators.new_email import DjangoEmailNotificator


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    telegram_notifications = providers.Container(
        TelegramNotificationsContainer,
        config=config
    )

    celery_events_repository = providers.Container(
        CeleryEventsRepositoryContainer
    )

    email_notificator = providers.Factory(
        DjangoEmailNotificator
    )

    services = providers.Container(
        DestinyServiceContainer
    )
    clients = providers.Container(
        ClientsContainer
    )
    bungie = providers.Container(
        BungieContainer
    )
    orders = providers.Container(
        OrdersContainer,
    )
    cart = providers.Container(
        ShoppingCartContainer
    )

    boosters = providers.Container(
        BoostersContainer
    )

    orders_uc = providers.Container(
        OrdersUseCases,
        telegram_notifications=telegram_notifications,
        orders=orders,
        services=services,
        clients=clients,
        bungie=bungie,
        email_notificator=email_notificator
    )
    cart_uc = providers.Container(
        ShoppingCartUseCases,
        services=services,
        bungie=bungie,
        clients=clients,
        orders=orders,
        cart=cart,
        celery_events_repository=celery_events_repository
    )

    client_dashboard_uc = providers.Container(
        ClientDashboardUcContainer,
        services=services,
        bungie=bungie,
        clients=clients,
        orders=orders,
        boosters=boosters,
    )
    use_cases = providers.Container(
        UseCases,
        services=services
    )
