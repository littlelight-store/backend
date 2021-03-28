from dependency_injector import containers, providers

from core.clients.application.repository import (
    ClientCredentialsRepository, ClientNotificationTokensRepository,
    ClientsRepository,
)


class ClientsContainer(containers.DeclarativeContainer):
    clients_repository = providers.ExternalDependency(ClientsRepository)
    clients_credentials_repository = providers.ExternalDependency(ClientCredentialsRepository)
    notification_tokens_repository = providers.ExternalDependency(ClientNotificationTokensRepository)
