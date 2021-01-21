from core.application.repositories.services import ServiceConfigsRepository, ServiceRepository
from core.domain.entities.service import service_options_price_calculator
from core.shopping_cart.application.repository import (
    PromoCodeRepository, ShoppingCartItemRepository,
    ShoppingCartRepository,
)
from core.shopping_cart.domain.promo_code import PromoCode, PromoCodeDoesNotExists
from core.shopping_cart.domain.shopping_cart import ShoppingCart, ShoppingCartItem
from core.shopping_cart.domain.types import ShoppingCartId


class ListCartItemsUseCaseMixin:
    """
    List all cart items with price
    """
    def __init__(
        self,
        cart_repository: ShoppingCartRepository,
        cart_item_repository: ShoppingCartItemRepository,
        service_repository: ServiceRepository,
        service_configs_repository: ServiceConfigsRepository,
        promo_code_repository: PromoCodeRepository

    ):
        self.promo_code_repository = promo_code_repository
        self.service_repository = service_repository
        self.cart_item_repository = cart_item_repository
        self.cart_repository = cart_repository
        self.service_configs_repository = service_configs_repository

    def calculate_price_for_cart_item(
        self,
        cart_item: ShoppingCartItem,
    ):
        service = self.service_repository.get_by_slug(cart_item.service_slug)
        service.set_price_resolver(service_options_price_calculator(service))

        cart_item.selected_options = self.service_configs_repository.list_by_shopping_cart_item(cart_item.id)
        total_price, total_old_price = service.get_service_price(
            options=cart_item.selected_options,
            range_options=cart_item.range_options,
        )

        cart_item.service = service
        cart_item.price = total_price
        cart_item.old_price = total_old_price

    def _apply_promo(self, cart: ShoppingCart) -> PromoCode:
        promo_code = None
        if cart.promo_id:
            try:
                promo_code = self.promo_code_repository.find_by_code(cart.promo_id)
                cart.apply_promo(promo_code)
            except PromoCodeDoesNotExists:
                pass
        return promo_code

    def get_shopping_cart_by_id(self, cart_id: ShoppingCartId) -> ShoppingCart:
        """
        @raise ShoppingCartDoesNotExists if cart not found
        """
        cart = self.cart_repository.get_by_id(cart_id)
        cart_items = self.cart_item_repository.get_by_shopping_cart(cart)
        self._apply_promo(cart)

        for cart_item in cart_items:
            self.calculate_price_for_cart_item(cart_item)

        cart.set_current_items(cart_items)
        return cart
