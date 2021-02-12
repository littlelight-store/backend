import typing as t
from pydantic import BaseModel

from core.application.repositories.services import ServiceConfigsRepository, ServiceRepository
from core.application.use_cases.dashboard.base_list_orders_dashboard import BaseListOrdersDashboard
from core.bungie.repositories import DestinyBungieCharacterRepository, DestinyBungieProfileRepository
from core.clients.application.dashboard.list_client_dashboard_use_case import (
    ClientDashboardSelectedOptions,
    ShortOrderModel,
)
from core.clients.application.repository import ClientCredentialsRepository
from core.clients.domain.client import ClientCredential
from core.order.application.repository import OrderObjectiveRepository
from core.utils.map_by_key import map_by_key
from profiles.constants import Membership


class ListBoosterDashboardDTOInput(BaseModel):
    booster_id: int


class ListBoosterDashboardDTOOutput(BaseModel):
    orders: t.List[ShortOrderModel]


class ClientCredentials(BaseModel):
    platform: Membership
    owner_id: int
    account_name: str
    account_password: str
    username: str


class BoosterShortOrderModelDTOOutput(ShortOrderModel):
    credentials: t.Optional[ClientCredentials]


class ListBoosterDashboardUseCase(BaseListOrdersDashboard):
    def __init__(
        self,
        order_objective_repository: OrderObjectiveRepository,
        destiny_bungie_profile_repository: DestinyBungieProfileRepository,
        destiny_character_repository: DestinyBungieCharacterRepository,
        service_repository: ServiceRepository,
        service_configs_repository: ServiceConfigsRepository,
        credentials_repository: ClientCredentialsRepository,
    ):
        self.credentials_repository = credentials_repository
        self.service_configs_repository = service_configs_repository
        self.service_repository = service_repository
        self.destiny_character_repository = destiny_character_repository
        self.destiny_bungie_profile_repository = destiny_bungie_profile_repository
        self.order_objective_repository = order_objective_repository

    def execute(self, dto: ListBoosterDashboardDTOInput) -> ListBoosterDashboardDTOOutput:
        objectives = self.order_objective_repository.list_by_booster(dto.booster_id)
        
        client_orders = [o.client_order_id for o in objectives]

        order_aggregated_data = self.get_aggregated_data(client_orders)

        result = ListBoosterDashboardDTOOutput(
            orders=[]
        )

        credentials = map_by_key(
            self.credentials_repository.list_by_booster_and_orders(dto.booster_id, client_orders),
            'owner_id'
        )

        for objective in objectives:
            character = order_aggregated_data['destiny_characters'][objective.destiny_character_id]
            profile = order_aggregated_data['destiny_profiles'][objective.destiny_profile_id]
            service = order_aggregated_data['services'][objective.service_slug]

            current_credentials: t.Optional[ClientCredential] = credentials.get(objective.client_id)

            result.orders.append(
                BoosterShortOrderModelDTOOutput(
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
                    created_at=objective.created_at,
                    credentials=ClientCredentials(
                        platform=current_credentials.platform,
                        account_name=current_credentials.account_name,
                        account_password=current_credentials.account_password,
                        owner_id=current_credentials.owner_id,
                        username=profile.username
                    ) if current_credentials and not objective.has_final_status() else None,
                    client_id=objective.client_id
                )
            )
        return result

