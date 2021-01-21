from asgiref.sync import sync_to_async

from core.application.repositories import OrderRepo, NotificationsRepository
from core.application.repositories.order import BoostersRepo
from core.domain.object_values import OrderId, DiscordId


class AssignBoosterToOrderUseCase:
    order_id: int
    booster_discord: str

    def __init__(
        self,
        order_repo: OrderRepo,
        boosters_repo: BoostersRepo,
        notification_repo: NotificationsRepository
    ):
        self.notification_repo = notification_repo
        self.order_repo = order_repo
        self.boosters_repo = boosters_repo

    def set_params(self, order_id: OrderId, booster_discord: DiscordId):
        self.order_id = order_id
        self.booster_discord = booster_discord
        return self

    @sync_to_async
    def execute(self):
        booster = self.boosters_repo.get_by_discord(self.booster_discord)

        order = self.order_repo.get_order(self.order_id)
        order.set_booster(booster)

        self.notification_repo.booster_assigned(order, booster)
        self.order_repo.update_order(order)
