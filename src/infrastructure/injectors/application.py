from dependency_injector import containers, providers

from core.clients.application.send_web_push import SendWebPushUseCase
from infrastructure.injectors.booster_dashboard_uc import BoosterDashboardUseCases
from infrastructure.injectors.boosters import BoostersContainer
from infrastructure.injectors.bungie import BungieContainer
from infrastructure.injectors.celery import CeleryEventsRepositoryContainer
from infrastructure.injectors.chat import ChatContainer
from infrastructure.injectors.client_dashboard_uc import ClientDashboardUcContainer
from infrastructure.injectors.clients import ClientsContainer
from infrastructure.injectors.notificators import TelegramNotificationsContainer
from infrastructure.injectors.orders import OrderStatusChangeUcContainer, OrdersContainer, OrdersUseCases
from infrastructure.injectors.services import DestinyServiceContainer
from infrastructure.injectors.shopping_cart import ShoppingCartContainer, ShoppingCartUseCases
from infrastructure.injectors.use_cases import UseCases
from notificators.discord import NewDiscordNotificator
from notificators.new_email import DjangoEmailNotificator
from notificators.web_push import GoogleWebPushNotifications


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    telegram_notifications = providers.Container(
        TelegramNotificationsContainer,
        config=config
    )
    google_web_push_notifications = providers.Factory(
        GoogleWebPushNotifications,
        token=config.google_fcm_token,
        dry_run=config.google_fcm_notifications_dry
    )

    celery_events_repository = providers.Container(
        CeleryEventsRepositoryContainer
    )

    email_notificator = providers.Factory(
        DjangoEmailNotificator
    )
    discord_notificator = providers.Factory(
        NewDiscordNotificator
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
    chat = providers.Container(
        ChatContainer,
        clients=clients,
        telegram_notifications=telegram_notifications,
        email_notificator=email_notificator,
        celery_events_repository=celery_events_repository
    )
    boosters = providers.Container(
        BoostersContainer
    )

    create_chat_message_uc = providers.Factory(
        SendWebPushUseCase,
        client_notification_tokens_repository=clients.notification_tokens_repository,
        push_service=google_web_push_notifications
    )

    orders_uc = providers.Container(
        OrdersUseCases,
        telegram_notifications=telegram_notifications,
        orders=orders,
        services=services,
        clients=clients,
        bungie=bungie,
        email_notificator=email_notificator,
        discord_notificator=discord_notificator
    )

    orders_status_uc = providers.Container(
        OrderStatusChangeUcContainer,
        telegram_notifications=telegram_notifications,
        orders=orders,
        services=services,
        clients=clients,
        email_notificator=email_notificator,
        boosters=boosters
    )

    cart_uc = providers.Container(
        ShoppingCartUseCases,
        services=services,
        bungie=bungie,
        clients=clients,
        orders=orders,
        cart=cart,
        celery_events_repository=celery_events_repository,
    )

    client_dashboard_uc = providers.Container(
        ClientDashboardUcContainer,
        services=services,
        bungie=bungie,
        clients=clients,
        orders=orders,
        boosters=boosters,
    )
    booster_dashboard_uc = providers.Container(
        BoosterDashboardUseCases,
        services=services,
        bungie=bungie,
        clients=clients,
        orders=orders,
        boosters=boosters,
        telegram_notifications=telegram_notifications
    )
    use_cases = providers.Container(
        UseCases,
        services=services,
        orders=orders
    )
