from dependency_injector import containers, providers

from core.clients.application.repository import ClientCredentialsRepository, ClientsRepository


class ClientsContainer(containers.DeclarativeContainer):
    clients_repository = providers.ExternalDependency(ClientsRepository)
    clients_credentials_repository = providers.ExternalDependency(ClientCredentialsRepository)