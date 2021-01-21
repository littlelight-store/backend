import logging

from core.application.dtos.notifications.event_notifications import EventOrderCreatedDTO
from core.application.repositories import EventNotificationRepository
from core.domain.entities.booster import Booster
from core.domain.entities.client import Client
from core.domain.entities.order import ParentOrder, Order
from notifications import (
    TelegramClient, send_telegram_message_order_created, send_order_not_created,
    send_booster_assigned,
)
from notificators.templates.telegram import get_new_order_message

logger = logging.getLogger(__name__)

ANDREY = "368801298"
STAS = "286739018"


class TelegramNotificator(EventNotificationRepository):
    def booster_assigned(self, order: Order, booster: Booster):
        send_booster_assigned.delay(
            order_id=order.id,
            booster_username=booster.username
        )

    def order_creation_failed(self, order_id: str):
        send_order_not_created.delay(
            order_id=order_id
        )

    def order_created(self, parent_order: ParentOrder, client: Client):
        """
        @deprecated Do not use
        """
        for order in parent_order.orders:
            send_telegram_message_order_created.delay(
                service=order.service.title,
                price=order.total_price,
                platform=parent_order.platform.name,
                char_class=order.character.character_class.name,
                promo=parent_order.promo.code if parent_order.promo else None,
                options=[o.dict() for o in order.service.options_representation],
                option=None,
                user_email=client.email,
                username=parent_order.bungie_profile.username
            )

    def new_order_created(self, dto: EventOrderCreatedDTO):
        send_telegram_message_order_created.delay(
            service=dto.service_title,
            price=dto.total_price,
            platform=dto.platform.name,
            char_class=dto.character_class.name,
            promo=dto.promo_code,
            options=[o.dict() for o in dto.options],
            option=None,
            user_email=dto.user_email,
            username=dto.username
        )


class TelegramNotificationsRepository(EventNotificationRepository):
    def __init__(self, client: TelegramClient):
        self.client = client

    def order_created(self, parent_order: ParentOrder, client: Client):
        pass

    def order_creation_failed(self, order_id: str):
        pass

    def booster_assigned(self, order: Order, booster: Booster):
        pass

    def new_order_created(self, dto: EventOrderCreatedDTO):
        logger.info(f"Sending new order created message")
        self.client.make_call(user_ids=[STAS, ANDREY], text=get_new_order_message(dto))
