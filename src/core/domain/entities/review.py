import typing as t

from core.domain.entities.interfaces import IClient
from core.domain.entities.order import Order, ParentOrder
from core.domain.object_values import ParentOrderId


class Review:
    def __init__(
        self,
        author: IClient,
        parent_order_id: ParentOrderId,
        orders: t.List['Order'] = list
    ):
        self.author = author
        self.parent_order_id = parent_order_id
        self.orders = orders

    @classmethod
    def create(cls, client: IClient, parent_order: ParentOrder):
        return cls(
            parent_order_id=parent_order.id,
            author=client,
            orders=parent_order.orders
        )
