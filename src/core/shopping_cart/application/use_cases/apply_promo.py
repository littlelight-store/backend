from pydantic import BaseModel

from core.application.repositories.services import ServiceConfigsRepository, ServiceRepository
from core.shopping_cart.application.repository import (
    PromoCodeRepository, ShoppingCartItemRepository,
    ShoppingCartRepository,
)
from core.shopping_cart.application.use_cases.dto import CartResponse, PromoCodeDTO
from core.shopping_cart.application.use_cases.list_cart_items_mixin import ListCartItemsUseCaseMixin
from core.shopping_cart.domain.promo_code import PromoCodeDoesNotExists
from core.shopping_cart.domain.types import ShoppingCartId


class ApplyPromoUseCaseDTOInput(BaseModel):
    code: str
    cart_id: ShoppingCartId


class ApplyPromoUseCaseDTOOutput(CartResponse):
    pass


class ApplyPromoUseCase(ListCartItemsUseCaseMixin):
    def __init__(
        self,
        shopping_cart_repository: ShoppingCartRepository,
        shopping_cart_items_repository: ShoppingCartItemRepository,
        service_repository: ServiceRepository,
        service_configs_repository: ServiceConfigsRepository,
        promo_code_repository: PromoCodeRepository
    ):
        self.promo_code_repository = promo_code_repository
        super().__init__(
            shopping_cart_repository, shopping_cart_items_repository,
            service_repository, service_configs_repository,
            promo_code_repository
        )

    def execute(self, dto: ApplyPromoUseCaseDTOInput):
        cart = self.get_shopping_cart_by_id(dto.cart_id)

        try:
            promo = self.promo_code_repository.find_by_code(dto.code)
        except PromoCodeDoesNotExists:
            promo = None

        cart.apply_promo(promo)

        self.cart_repository.update(cart)

        total_price, total_old_price = cart.prices

        return ApplyPromoUseCaseDTOOutput(
            total_price=total_price,
            total_old_price=total_old_price,
            cart_id=cart.id,
            promo_code=PromoCodeDTO.from_entity(promo) if promo else None
        )

