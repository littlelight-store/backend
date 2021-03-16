import logging

from boosting.settings import IS_PROD
from core.application.dtos.notifications.event_notifications import EventChatMessageDTO, EventOrderCreatedDTO
from core.application.repositories import EventNotificationRepository
from core.application.repositories.notifications import BoosterAssignedNotificationDTO
from core.domain.entities.client import Client
from core.domain.entities.order import ParentOrder
from notifications import (
    TelegramClient, broadcast_message,
)
from notificators.templates.telegram import get_new_order_message, get_new_chat_message, get_booster_assigned_message

logger = logging.getLogger(__name__)

ANDREY = "368801298"
STAS = "286739018"


class TelegramNotificationsRepository(EventNotificationRepository):

    def chat_message(self, dto: EventChatMessageDTO):
        from notifications import new_chat_message

        if IS_PROD:
            logger.info(f"Sending new chat")
            new_chat_message.delay(
                text=get_new_chat_message(dto)
            )

    def __init__(self, client: TelegramClient):
        self.client = client

    def order_created(self, parent_order: ParentOrder, client: Client):
        pass

    def order_creation_failed(self, order_id: str):
        pass

    def new_order_created(self, dto: EventOrderCreatedDTO):
        logger.info(f"Sending new order created message")
        self.client.make_call(user_ids=[STAS, ANDREY], text=get_new_order_message(dto))

    def booster_assigned(self, dto: BoosterAssignedNotificationDTO):
        self.client.make_call(user_ids=[STAS, ANDREY], text=get_booster_assigned_message(dto))
