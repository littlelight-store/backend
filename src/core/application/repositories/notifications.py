import datetime as dt
import abc
import typing as t
from decimal import Decimal

from pydantic import BaseModel

from core.application.dtos.notifications.event_notifications import (
    EventChatMessageDTO, EventOrderCreatedDTO,
    EventOrderCreatedOptionDTO,
)
from core.domain.entities.client import Client
from core.domain.entities.order import ParentOrder
from notificators.constants import Category
from profiles.constants import Membership


class BoosterAssignedNotificationDTO(BaseModel):
    booster_username: str
    order_id: str
    order_service: str


class EventNotificationRepository(abc.ABC):

    @abc.abstractmethod
    def order_created(self, parent_order: ParentOrder, client: Client): ...

    @abc.abstractmethod
    def order_creation_failed(self, order_id: str): ...

    @abc.abstractmethod
    def booster_assigned(self, dto: BoosterAssignedNotificationDTO): ...

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
    selected_services: t.List[EventOrderCreatedOptionDTO]
    order_id: str
    platform: Membership
    category: Category
    booster_price: Decimal
    client_username: str


class OrderExecutorsNotificationRepository(abc.ABC):

    @abc.abstractmethod
    def order_created(self, dto: OrderCreatedDTO): ...
