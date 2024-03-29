import typing as t
from pydantic import BaseModel
import datetime as dt

from core.application.repositories.services import ServiceConfigsRepository, ServiceRepository
from core.application.use_cases.dashboard.base_list_orders_dashboard import BaseListOrdersDashboard
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
    user_id: int


class ShortOrderModel(BaseModel):
    membership_type: Membership
    character_class: CharacterClasses
    username: str

    service_title: str
    total_price: str

    service_image: str

    selected_options: t.List[ClientDashboardSelectedOptions]
    booster: t.Optional[dict] = None
    status: OrderObjectiveStatus
    order_id: str
    order_objective_id: str
    created_at: dt.datetime
    client_id: int

    progress: int = 0


class ProfilePlatformCredential(BaseModel):
    platform: Membership
    must_be_set: bool
    is_set: bool
    account_name: t.Optional[str]
    owner_id: int
    has_second_factor: bool


class ListClientDashboardUseCaseDTOOutput(BaseModel):
    orders: t.List[ShortOrderModel]
    credentials: t.List[ProfilePlatformCredential]


IGNORED_PLATFORMS = [Membership.BattleNET]


class ListClientDashboardUseCase(BaseListOrdersDashboard):
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
                is_expired = False
                has_second_factor = False

                if v in current_credentials:
                    credentials = current_credentials[v]
                    account_name = credentials.account_name
                    is_set = True
                    is_expired = credentials.is_expired
                    has_second_factor = credentials.has_second_factor

                if v in platforms_in_orders:
                    must_be_set = not is_set

                credentials = ProfilePlatformCredential(
                    platform=v,
                    is_set=is_set,
                    must_be_set=is_expired or must_be_set,
                    account_name=account_name,
                    owner_id=client_id,
                    has_second_factor=bool(has_second_factor)
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

        order_aggregated_data = self.get_aggregated_data(client_orders)

        boosters = map_by_key(
            self.boosters_repository.list_by_client_orders(dto.client_id),
            'id'
        )

        platforms = set()

        for objective in objectives:
            character = order_aggregated_data['destiny_characters'][objective.destiny_character_id]
            profile = order_aggregated_data['destiny_profiles'][objective.destiny_profile_id]
            service = order_aggregated_data['services'][objective.service_slug]

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
                            title=order_aggregated_data['service_configs'][s].title
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
                        rating=booster.rating,
                        user_id=booster.user_id
                    ) if booster else None,
                    client_id=objective.client_id,
                    created_at=objective.created_at
                )
            )

        result.credentials = self._form_credentials_response_part(dto.client_id, platforms)

        return result
