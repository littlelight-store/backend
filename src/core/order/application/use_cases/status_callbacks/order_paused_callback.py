from pydantic import BaseModel

from core.boosters.application.repository import BoostersRepository
from core.clients.application.repository import ClientsRepository
from core.order.application.repository import OrderObjectiveRepository
from core.utils.map_by_key import map_by_key
from notificators.new_email import DjangoEmailNotificator, PausedOrder


class BoosterPausedOrderDTORequest(BaseModel):
    order_objective_id: str
    client_id: int


class BoosterPausedOrderUseCase:
    def __init__(
        self,
        email_notificator: DjangoEmailNotificator,
        order_objectives_repository: OrderObjectiveRepository,
        clients_repository: ClientsRepository,
        boosters_repository: BoostersRepository
    ):
        self.boosters_repository = boosters_repository
        self.clients_repository = clients_repository
        self.order_objectives_repository = order_objectives_repository
        self.email_notificator = email_notificator

    def execute(self, dto: BoosterPausedOrderDTORequest):
        objective = self.order_objectives_repository.get_by_user_and_id(
            order_objective_id=dto.order_objective_id,
            client_id=dto.client_id
        )

        boosters = map_by_key(
            self.boosters_repository.list_by_client_orders(dto.client_id),
            'id'
        )

        username = 'Booster'
        if objective.booster_id:
            booster = boosters[objective.booster_id]
            if booster:
                username = booster.username

        client = self.clients_repository.get_by_id(objective.client_id)

        self.email_notificator.send_paused_order(
            PausedOrder(
                user_email=client.email,
                booster_username=username
            )
        )
