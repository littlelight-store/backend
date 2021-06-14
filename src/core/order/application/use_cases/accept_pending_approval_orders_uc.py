import datetime as dt
import logging
from dataclasses import dataclass

from core.order.application.repository import OrderObjectiveRepository

logger = logging.getLogger(__name__)


@dataclass
class AcceptPendingApprovalOrdersDTORequest:
    now: dt.datetime


class AcceptPendingApprovalOrdersUseCase:
    def __init__(
        self,
        order_objectives_repository: OrderObjectiveRepository
    ):
        self.order_objectives_repository = order_objectives_repository

    def execute(self, dto: AcceptPendingApprovalOrdersDTORequest):
        objectives = self.order_objectives_repository.list_pending_approval_orders()

        for o in objectives:
            if o.must_be_auto_accepted(dto.now):
                logger.info(f"Order objective: {o.id} must be accepted")
                o.completed()
                self.order_objectives_repository.save(o)
