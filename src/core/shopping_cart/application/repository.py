import typing as t
import abc

from core.shopping_cart.domain.promo_code import PromoCode
from core.shopping_cart.domain.shopping_cart import ShoppingCart, ShoppingCartItem
from core.shopping_cart.domain.types import ShoppingCartId


class ShoppingCartRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(
        self,
        shopping_cart_id: str,
    ) -> ShoppingCart:
        """
        @raise ShoppingCartDoesNotExists if cart is not found
        """
        pass

    @abc.abstractmethod
    def create(
        self,
        shopping_cart: ShoppingCart
    ) -> t.NoReturn:
        pass

    @abc.abstractmethod
    def delete(self, shopping_cart_id: str):
        pass

    @abc.abstractmethod
    def update(self, shopping_cart: ShoppingCart) -> t.NoReturn:
        pass


class ShoppingCartItemRepository(abc.ABC):

    @abc.abstractmethod
    def create(
        self,
        item: ShoppingCartItem,
        options: t.List[int],
    ) -> ShoppingCartItem:
        pass

    @abc.abstractmethod
    def get_by_shopping_cart(self, shopping_cart: ShoppingCart) -> t.List[ShoppingCartItem]:
        pass

    @abc.abstractmethod
    def delete(self, cart_item_id: str, shopping_cart_id: str):
        pass

    @abc.abstractmethod
    def delete_by_shopping_cart(self, shopping_cart_id: ShoppingCartId):
        pass


class PromoCodeRepository(abc.ABC):
    @abc.abstractmethod
    def find_by_code(self, code: str) -> PromoCode:
        """
        @raise PromoCodeDoesNotExists if code not found
        """
        pass
