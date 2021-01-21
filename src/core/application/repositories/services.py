import typing as t
import abc

from core.domain.entities.service import Service, ServiceConfig, ServiceDetailedInfo, ServiceGroupTag


class ServiceRepository(abc.ABC):

    @abc.abstractmethod
    def list_active(self) -> t.Dict[ServiceGroupTag, t.List[Service]]: ...

    @abc.abstractmethod
    def get_by_slug(self, slug: str) -> Service:
        pass

    @abc.abstractmethod
    def list_by_client_order(self, client_order: str) -> t.List[Service]:
        pass

    @abc.abstractmethod
    def list_by_client_orders(self, client_orders: t.List[str]) -> t.List[Service]:
        pass


class ServiceConfigsRepository(abc.ABC):
    @abc.abstractmethod
    def list_by_client_orders(self, client_orders: t.List[str]) -> t.List[ServiceConfig]:
        pass

    @abc.abstractmethod
    def list_by_service(self, service_slug: str) -> t.List[ServiceConfig]:
        pass

    @abc.abstractmethod
    def list_by_shopping_cart_item(self, cart_item_id: str) -> t.List[ServiceConfig]:
        pass

    @abc.abstractmethod
    def map_by_client_order(self, client_order: str) -> t.Dict[str, t.List[ServiceConfig]]:
        pass


class ServiceDetailedInfoRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_slug(self, service_slug: str) -> ServiceDetailedInfo:
        pass
