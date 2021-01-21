import abc
import datetime as dt
import typing as t
from decimal import Decimal

from core.domain.object_values import ClientId, BoosterId, DiscordId, OrderId
from orders.enum import OrderStatus
from orders.parse_product_options import TemplateRepresentation


class IServiceConfig(abc.ABC):
    title: str
    id: int
    description: str
    price: Decimal
    old_price: Decimal
    extra_data: dict


class IService(abc.ABC):
    title: str
    slug: str
    layout_options: t.Optional[t.Dict[str, t.Dict[t.Any, t.Any]]]
    price: Decimal
    options_ids: t.List[str]
    configs: t.List['IServiceConfig']
    booster_price: Decimal
    booster_percent: int
    options_representation: t.List[TemplateRepresentation]
    product_link: str
    category: str


class IUser(abc.ABC):
    pass


class IBooster(abc.ABC):
    id: BoosterId
    discord_id: DiscordId


class IClient(abc.ABC):
    email: str
    client_id: t.Optional[ClientId] = None


class IOrder(abc.ABC):
    service: IService
    booster_user_id: t.Optional[IBooster]
    created_at: dt.datetime
    booster_price: Decimal
    status: OrderStatus
    id: OrderId

