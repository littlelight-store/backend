import typing as t
from pydantic import BaseModel

from core.application.repositories.services import ServiceConfigsRepository, ServiceRepository
from core.boosters.application.repository import BoostersRepository
from core.bungie.entities import DestinyBungieProfile, DestinyCharacter
from core.bungie.repositories import DestinyBungieCharacterRepository, DestinyBungieProfileRepository
from core.clients.application.repository import ClientCredentialsRepository
from core.domain.entities.service import Service, ServiceConfig
from core.order.application.repository import ClientOrderRepository, OrderObjectiveRepository
from core.order.domain.consts import OrderObjectiveStatus
from core.utils.map_by_key import map_by_key
from profiles.constants import CharacterClasses, Membership


class ListClientDashboardUseCaseDTOInput(BaseModel):
    client_id: int


class ClientDashboardSelectedOptions(BaseModel):
    title: str


class BoosterInfo(BaseModel):
    id: str
    username: str
    rating: float
    avatar: t.Optional[str]


class ShortOrderModel(BaseModel):
    membership_type: Membership
    character_class: CharacterClasses
    username: str

    service_title: str
    total_price: str

    service_image: str

    selected_options: t.List[ClientDashboardSelectedOptions]
    booster: t.Optional[dict]
    status: OrderObjectiveStatus
    order_id: str
    order_objective_id: str

    progress: int = 0


class ProfilePlatformCredential(BaseModel):
    platform: Membership
    must_be_set: bool
    is_set: bool
    account_name: t.Optional[str]
    owner_id: int


class ListClientDashboardUseCaseDTOOutput(BaseModel):
    orders: t.List[ShortOrderModel]
    credentials: t.List[ProfilePlatformCredential]


IGNORED_PLATFORMS = [Membership.BattleNET]


class ListClientDashboardUseCase:
    def __init__(
        self,
        destiny_bungie_profile_repository: DestinyBungieProfileRepository,
        destiny_character_repository: DestinyBungieCharacterRepository,
        service_repository: ServiceRepository,
        service_configs_repository: ServiceConfigsRepository,
        order_repository: ClientOrderRepository,
        order_objective_repository: OrderObjectiveRepository,
        client_credentials_repository: ClientCredentialsRepository,
        boosters_repository: BoostersRepository
    ):
        self.boosters_repository = boosters_repository
        self.client_credentials_repository = client_credentials_repository
        self.order_objective_repository = order_objective_repository
        self.order_repository = order_repository
        self.service_configs_repository = service_configs_repository
        self.service_repository = service_repository
        self.destiny_character_repository = destiny_character_repository
        self.destiny_bungie_profile_repository = destiny_bungie_profile_repository

    def _form_credentials_response_part(
        self,
        client_id: int,
        platforms_in_orders: t.Set[Membership]
    ) -> t.List[ProfilePlatformCredential]:
        current_credentials = map_by_key(
            self.client_credentials_repository.list_by_user(client_id),
            'platform'
        )

        result = []

        for v in Membership:
            if v not in IGNORED_PLATFORMS:
                is_set = False
                must_be_set = False
                account_name = None

                if v in current_credentials:
                    account_name = current_credentials[v].account_name
                    is_set = True

                if v in platforms_in_orders:
                    must_be_set = not is_set

                credentials = ProfilePlatformCredential(
                    platform=v,
                    is_set=is_set,
                    must_be_set=must_be_set,
                    account_name=account_name,
                    owner_id=client_id
                )
                result.append(credentials)

        return result

    def execute(self, dto: ListClientDashboardUseCaseDTOInput) -> ListClientDashboardUseCaseDTOOutput:
        orders = self.order_repository.list_by_user(dto.client_id)

        result = ListClientDashboardUseCaseDTOOutput(
            orders=[],
            credentials=[]
        )
        client_orders = [o.id for o in orders]

        objectives = self.order_objective_repository.list_by_orders(client_orders)

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

        boosters = map_by_key(
            self.boosters_repository.list_by_client_orders(dto.client_id),
            'id'
        )

        platforms = set()

        for objective in objectives:
            character = destiny_characters[objective.destiny_character_id]
            profile = destiny_profiles[objective.destiny_profile_id]
            service = services[objective.service_slug]
            booster = boosters[objective.booster_id] if objective.booster_id else None
            platforms.add(profile.membership_type)
            result.orders.append(
                ShortOrderModel(
                    membership_type=profile.membership_type,
                    username=profile.username,
                    character_class=character.character_class,
                    service_title=service.title,
                    service_image=service.item_image,
                    total_price=objective.price,
                    selected_options=[
                        ClientDashboardSelectedOptions(
                            title=service_configs[s].title
                        )
                        for s in objective.selected_option_ids
                    ],
                    status=objective.status,
                    order_id=objective.client_order_id,
                    order_objective_id=objective.id,
                    booster=BoosterInfo(
                        id=booster.id,
                        avatar=booster.avatar,
                        username=booster.username,
                        rating=booster.rating
                    ) if booster else None
                )
            )

        result.credentials = self._form_credentials_response_part(dto.client_id, platforms)

        return result
