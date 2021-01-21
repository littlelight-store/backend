from dependency_injector import containers, providers

from notifications import TelegramClient
from notificators.telegram import TelegramNotificationsRepository


class TelegramNotificationsContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    client = providers.Factory(
        TelegramClient,
        telegram_token=config.BOT_TOKEN
    )

    repository = providers.Factory(
        TelegramNotificationsRepository,
        client=client
    )
