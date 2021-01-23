import abc
import typing as t

from core.order.domain.order import ClientOrder, ClientOrderObjective
from core.shopping_cart.domain.types import ShoppingCartId


class ClientOrderRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, order_id: str) -> ClientOrder:
        pass

    @abc.abstractmethod
    def list_by_user(self, user_id: int) -> t.List[ClientOrder]:
        pass

    @abc.abstractmethod
    def create(
        self,
        order: ClientOrder
    ) -> t.NoReturn:
        pass

    @abc.abstractmethod
    def get_by_cart_id(self, cart_id: ShoppingCartId) -> ClientOrder:
        pass

    @abc.abstractmethod
    def save(self, client_order: ClientOrder):
        pass


class OrderObjectiveRepository(abc.ABC):
    @abc.abstractmethod
    def create_bulk(
        self,
        order_objectives: t.List[ClientOrderObjective],
    ):
        pass

    @abc.abstractmethod
    def list_by_orders(self, order_ids: t.List[str]) -> t.List[ClientOrderObjective]:
        pass

    @abc.abstractmethod
    def get_by_order(self, order_id: str) -> t.List[ClientOrderObjective]:
        pass

    @abc.abstractmethod
    def save(self, order: ClientOrderObjective):
        pass


class MQEventsRepository(abc.ABC):

    @abc.abstractmethod
    def new_order_created(self, client_order_id: str):
        pass
