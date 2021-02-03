import enum

from pydantic import BaseModel

from core.order.application.repository import OrderObjectiveRepository
from core.order.domain.consts import OrderObjectiveStatus
from core.order.domain.order import ClientOrderObjective


class ClientStatusDispatcherAction(str, enum.Enum):
    approve_order = 'approve_order'  # Accept order as complete
    accept_order = 'accept_order'  # Booster accepts order
    booster_signed_in = 'booster_signed_in'  # Booster is authorized
    in_progress = 'in_progress'  # Booster is authorized
    booster_invalid_credentials = 'booster_invalid_credentials'  # Credentials are invalid
    booster_required_2_fa = 'booster_required_2_fa'  # 2 FA Required by booster
    booster_order_completed = 'booster_order_completed'  # Booster completed an order


class OrderStatusDispatcherDTORequest(BaseModel):
    action: ClientStatusDispatcherAction
    order_objective_id: str
    client_id: int


class OrderStatusDispatcherDTOOutput(BaseModel):
    status: OrderObjectiveStatus


class OrderStatusDispatcher:
    def __init__(
        self,
        order_objective_repository: OrderObjectiveRepository,
    ):
        self.order_objectives_repository = order_objective_repository

    def set_next_status_by_action(
        self,
        order_objective: ClientOrderObjective,
        action: ClientStatusDispatcherAction
    ):
        if action == ClientStatusDispatcherAction.approve_order:
            order_objective.completed()
        elif action == ClientStatusDispatcherAction.accept_order:
            order_objective.booster_accepted()
        elif action == ClientStatusDispatcherAction.booster_signed_in:
            order_objective.in_progress()
        elif action == ClientStatusDispatcherAction.booster_invalid_credentials:
            order_objective.invalid_credentials()
        elif action == ClientStatusDispatcherAction.booster_required_2_fa:
            order_objective.required_2fa_code()
        elif action == ClientStatusDispatcherAction.booster_order_completed:
            order_objective.status = OrderObjectiveStatus.PENDING_APPROVAL
            self.order_objectives_repository.save(order_objective)
            order_objective.pending_approval()

    def execute(self, dto: OrderStatusDispatcherDTORequest):
        objective = self.order_objectives_repository.get_by_user_and_id(dto.order_objective_id, dto.client_id)
        self.set_next_status_by_action(objective, dto.action)
        self.order_objectives_repository.save(objective)

        return OrderStatusDispatcherDTOOutput(
            status=objective.status
        )
