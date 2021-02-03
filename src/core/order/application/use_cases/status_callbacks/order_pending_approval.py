import datetime as dt
import logging

from pydantic import BaseModel

from core.application.repositories import EventNotificationRepository
from core.application.repositories.services import ServiceRepository
from core.clients.application.repository import ClientsRepository
from core.order.application.repository import ClientOrderRepository, OrderObjectiveRepository
from core.order.domain.order import ClientOrderStatus
from core.utils.map_by_key import map_by_key
from notificators.new_email import DjangoEmailNotificator, PendingApprovalNotification

logger = logging.getLogger(__name__)


class OrderPendingApprovalCallbackDTORequest(BaseModel):
    order_objective_id: str


class OrderPendingApprovalCallbackUseCase:
    def __init__(
        self,
        event_notifications_repository: EventNotificationRepository,
        client_orders_repository: ClientOrderRepository,
        order_objectives_repository: OrderObjectiveRepository,
        services_repository: ServiceRepository,
        clients_repository: ClientsRepository,
        email_notificator: DjangoEmailNotificator
    ):
        self.email_notificator = email_notificator
        self.services_repository = services_repository
        self.event_notifications_repository = event_notifications_repository
        self.clients_repository = clients_repository
        self.order_objectives_repository = order_objectives_repository
        self.client_orders_repository = client_orders_repository

    def execute(self, dto: OrderPendingApprovalCallbackDTORequest):
        client_order = self.client_orders_repository.get_by_order_objective(dto.order_objective_id)
        order_objectives = self.order_objectives_repository.get_by_order(client_order.id)

        total_on_complete_statuses = set()

        for objective in order_objectives:
            if objective.has_final_status():
                total_on_complete_statuses.add(objective.id)

        print(total_on_complete_statuses, order_objectives)

        if len(total_on_complete_statuses) == len(order_objectives):
            logger.info(
                'All child orders are complete. '
                'Marking parent order as pending approval and sending and email'
            )

            services = map_by_key(
                self.services_repository.list_by_client_order(client_order.id),
                'slug'
            )
            client = self.clients_repository.get_by_id(client_order.client_id)

            services_reprs = []

            for objective in order_objectives:
                service = services[objective.service_slug]
                services_reprs.append(f"{service.title} — ${objective.price}")

            client_order.order_status = ClientOrderStatus.PENDING_APPROVAL
            client_order.order_status_changed_at = dt.datetime.utcnow()

            self.client_orders_repository.save(client_order)

            self.email_notificator.send_pending_approval(
                PendingApprovalNotification(
                    services=services_reprs,
                    user_email=client.email
                )
            )
