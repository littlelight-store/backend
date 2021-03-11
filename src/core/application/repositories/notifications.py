import datetime as dt
import abc
import typing as t

from pydantic import BaseModel

from core.application.dtos.notifications.event_notifications import (
    EventChatMessageDTO, EventOrderCreatedDTO,
    EventOrderCreatedOptionDTO,
)
from core.domain.entities.booster import Booster
from core.domain.entities.client import Client
from core.domain.entities.order import ParentOrder, Order
from core.order.domain.order import ClientOrder
from core.shopping_cart.application.use_cases.dto import CartObjectiveDataDTO
from notificators.constants import Category
from profiles.constants import Membership


class EventNotificationRepository(abc.ABC):

    @abc.abstractmethod
    def order_created(self, parent_order: ParentOrder, client: Client): ...

    @abc.abstractmethod
    def order_creation_failed(self, order_id: str): ...

    @abc.abstractmethod
    def booster_assigned(self, order: Order, booster: Booster): ...

    @abc.abstractmethod
    def new_order_created(self, dto: EventOrderCreatedDTO): ...

    @abc.abstractmethod
    def chat_message(self, param: EventChatMessageDTO):
        pass


class ClientNotificationRepository(abc.ABC):

    @abc.abstractmethod
    def order_created(self, parent_order: ParentOrder, client: Client): ...


class OrderCreatedDTO(BaseModel):
    service_title: str
    created_at: dt.datetime
    selected_services: list
    order_id: str
    platform: Membership
    category: Category
    booster_price: str


class OrderExecutorsNotificationRepository(abc.ABC):

    @abc.abstractmethod
    def order_created(self, dto: OrderCreatedDTO): ...


class NotificationsRepository:
    def __init__(
        self,
        event_repository: EventNotificationRepository,
        client_notification_repository: ClientNotificationRepository,
    ):
        self.client_notification_repository = client_notification_repository
        self.event_repository = event_repository

    def order_created(self, parent_order: ParentOrder, client: Client, with_notification: bool = False):
        if with_notification:
            self.event_repository.order_created(parent_order, client)
        self.client_notification_repository.order_created(parent_order, client)

    def new_order_created(
        self,
        order: ClientOrder,
        objectives: t.List[CartObjectiveDataDTO],
        user_email: str,
        username: str
    ):

        for obj in objectives:

            opts = [EventOrderCreatedOptionDTO(
                description=o.title,
                price=o.price
            ) for o in obj.selected_options]

            if obj.range_configs:
                points_from = obj.range_configs.get("pointsFrom")
                points_to = obj.range_configs.get("pointsTo")
                total_price = obj.range_configs.get("totalPrice")
                opts.append(
                    EventOrderCreatedOptionDTO(
                        description=f'From: {points_from} To: {points_to}',
                        price=total_price
                    )
                )

            self.event_repository.new_order_created(
                EventOrderCreatedDTO(
                    service_title=obj.service_title,
                    total_price=str(obj.price),
                    character_class=obj.character_class,
                    platform=order.platform,
                    promo_code=obj.promo_id,
                    user_email=user_email,
                    username=username,
                    options=opts
                )
            )

    def booster_assigned(self, order: Order, booster: Booster):
        self.event_repository.booster_assigned(order, booster)
