import typing as t

from typing_extensions import TypedDict

from core.application.repositories.services import ServiceConfigsRepository, ServiceRepository
from core.boosters.application.repository import BoostersRepository
from core.bungie.entities import DestinyBungieProfile
from core.bungie.repositories import DestinyBungieCharacterRepository, DestinyBungieProfileRepository
from core.domain.entities.bungie_profile import DestinyCharacter
from core.domain.entities.service import Service, ServiceConfig
from core.utils.map_by_key import map_by_key


class OrdersAggregatedData(TypedDict):
    destiny_characters: t.Dict[str, DestinyCharacter]
    destiny_profiles: t.Dict[str, DestinyBungieProfile]
    services: t.Dict[str, Service]
    service_configs: t.Dict[int, ServiceConfig]


class BaseListOrdersDashboard:
    destiny_bungie_profile_repository: DestinyBungieProfileRepository
    destiny_character_repository: DestinyBungieCharacterRepository
    service_repository: ServiceRepository
    service_configs_repository: ServiceConfigsRepository
    boosters_repository: BoostersRepository

    def get_aggregated_data(self, client_orders: t.List[str]) -> OrdersAggregatedData:
        destiny_characters: t.Dict[str, DestinyCharacter] = map_by_key(
            self.destiny_character_repository.list_by_orders(client_orders), 'character_id'
        )
        destiny_profiles: t.Dict[str, DestinyBungieProfile] = map_by_key(
            self.destiny_bungie_profile_repository.list_by_orders(client_orders), 'membership_id'
        )
        services: t.Dict[str, Service] = map_by_key(
            self.service_repository.list_by_client_orders(client_orders),
            'slug'
        )
        service_configs: t.Dict[int, ServiceConfig] = map_by_key(
            self.service_configs_repository.list_by_client_orders(client_orders),
            'id'
        )

        return OrdersAggregatedData(
            destiny_characters=destiny_characters,
            destiny_profiles=destiny_profiles,
            services=services,
            service_configs=service_configs
        )
