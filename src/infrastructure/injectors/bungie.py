from dependency_injector import containers, providers

from core.bungie.repositories import DestinyBungieCharacterRepository, DestinyBungieProfileRepository


class BungieContainer(containers.DeclarativeContainer):
    characters_repository = providers.ExternalDependency(
        DestinyBungieCharacterRepository
    )
    profiles_repository = providers.ExternalDependency(
        DestinyBungieProfileRepository
    )
