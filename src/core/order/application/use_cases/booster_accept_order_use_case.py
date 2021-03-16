from pydantic import BaseModel

from core.application.repositories import EventNotificationRepository
from core.application.repositories.notifications import BoosterAssignedNotificationDTO
from core.boosters.application.repository import BoostersRepository
from core.boosters.domain.entities import Booster
from core.order.application.repository import OrderObjectiveRepository
from core.order.domain.order import ClientOrderObjective


class BoosterAcceptOrderDTORequest(BaseModel):
    order_objective_id: str
    booster_user_id: int


def get_event_notification_repository_dto(
    booster: Booster,
    order_objective: ClientOrderObjective
):
    return BoosterAssignedNotificationDTO(
        booster_username=booster.username,
        order_id=order_objective.id,
        order_service=order_objective.service_slug
    )


class BoosterAcceptOrderUseCase:
    def __init__(
        self,
        boosters_repository: BoostersRepository,
        order_objective_repository: OrderObjectiveRepository,
        event_notifications_repository: EventNotificationRepository
    ):
        self.event_notifications_repository = event_notifications_repository
        self.order_objectives_repository = order_objective_repository
        self.boosters_repository = boosters_repository

    def execute(self, dto: BoosterAcceptOrderDTORequest):
        """
        @raise OrderIsAlreadyAccepted: if order is already taken
        @raise BoosterNotExists: if booster is not found
        """
        booster_profile = self.boosters_repository.get_by_user_id(dto.booster_user_id)
        order_objective = self.order_objectives_repository.get_by_id(dto.order_objective_id)
        order_objective.assign_booster(booster_profile.id)
        self.event_notifications_repository.booster_assigned(get_event_notification_repository_dto(
            booster_profile, order_objective
        ))
        self.order_objectives_repository.save(order_objective)

