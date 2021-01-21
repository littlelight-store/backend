from dependency_injector import providers
from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    name = 'profiles'

    def ready(self):
        from boosting import container
        from profiles.repository import (
            DjangoDestinyBungieProfileRepository, DjangoDestinyCharacterRepository, DjangoClientRepository,
            DjangoProfileCredentialsRepository, DjangoDestinyBoostersRepository
        )

        container.clients.clients_repository.override(providers.Factory(
            DjangoClientRepository
        ))
        container.clients.clients_credentials_repository.override(providers.Factory(
            DjangoProfileCredentialsRepository
        ))
        container.bungie.characters_repository.override(providers.Factory(
            DjangoDestinyCharacterRepository
        ))
        container.bungie.profiles_repository.override(providers.Factory(
            DjangoDestinyBungieProfileRepository
        ))
        container.boosters.repository.override(providers.Factory(
            DjangoDestinyBoostersRepository
        ))
