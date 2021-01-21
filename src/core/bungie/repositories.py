import typing as t
import abc

from core.bungie.entities import DestinyBungieProfile, DestinyCharacter
from core.shopping_cart.domain.types import ShoppingCartId


class DestinyBungieProfileRepository(abc.ABC):

    @abc.abstractmethod
    def bulk_link_with_client_id(
        self,
        client_id: int,
        bungie_profile_ids: t.List[str],
    ) -> t.NoReturn:
        pass

    @abc.abstractmethod
    def list_by_client(self, client_id: int) -> t.List[DestinyBungieProfile]:
        pass

    @abc.abstractmethod
    def get_by_id(self, membership_id: str) -> DestinyBungieProfile:
        pass

    @abc.abstractmethod
    def create_or_update(self, profile: DestinyBungieProfile):
        pass

    @abc.abstractmethod
    def get_by_cart_id(self, cart_id: ShoppingCartId) -> t.List[DestinyBungieProfile]:
        pass

    @abc.abstractmethod
    def list_by_client_order_id(self, client_order_id: str) -> t.List[DestinyBungieProfile]:
        pass

    @abc.abstractmethod
    def list_by_orders(self, order_ids: t.List[str]) -> t.List[DestinyBungieProfile]:
        pass


class DestinyBungieCharacterRepository(abc.ABC):
    @abc.abstractmethod
    def create_or_update(self, character: DestinyCharacter):
        pass

    @abc.abstractmethod
    def get_by_id(self, character_id: str) -> DestinyCharacter:
        pass

    @abc.abstractmethod
    def list_by_client_order_id(self, client_order_id: str) -> t.List[DestinyCharacter]:
        pass

    @abc.abstractmethod
    def list_by_client(self, client_id: int) -> t.List[DestinyCharacter]:
        pass

    @abc.abstractmethod
    def list_by_orders(self, order_ids: t.List[str]) -> t.List[DestinyCharacter]:
        pass
