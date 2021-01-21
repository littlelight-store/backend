import datetime as dt
from pydantic import BaseModel

from core.order.application.repository import ClientOrderRepository, OrderObjectiveRepository
from core.order.domain.order import ClientOrderStatus


class ProcessPaymentCallbackDTORequest(BaseModel):
    cart_id: str
    total_price: str


class ProcessPaymentCallbackUseCase:
    def __init__(
        self,
        client_orders_repository: ClientOrderRepository,
        order_objectives_repository: OrderObjectiveRepository
    ):
        self.client_orders_repository = client_orders_repository
        self.order_objectives_repository = order_objectives_repository

    def execute(self, dto: ProcessPaymentCallbackDTORequest):
        order = self.client_orders_repository.get_by_cart_id(dto.cart_id)
        objectives = self.order_objectives_repository.get_by_order(order.id)

        order.order_status = ClientOrderStatus.PAYED
        order.order_status_changed_at = dt.datetime.now()

        for objective in objectives:
            objective.status_controller.processing()
            self.order_objectives_repository.save(objective)

