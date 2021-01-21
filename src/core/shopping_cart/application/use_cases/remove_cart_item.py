from pydantic import BaseModel

from core.application.repositories.services import ServiceConfigsRepository, ServiceRepository
from core.shopping_cart.application.repository import (
    PromoCodeRepository, ShoppingCartItemRepository,
    ShoppingCartRepository,
)
from core.shopping_cart.application.use_cases.dto import CartResponse, PromoCodeDTO
from core.shopping_cart.application.use_cases.list_cart_items_mixin import ListCartItemsUseCaseMixin


class RemoveCartItemDTOInput(BaseModel):
    cart_id: str
    cart_item_id: str


class RemoveCartItemDTOOutput(CartResponse):
    success: bool


class RemoveCartItemUseCase(ListCartItemsUseCaseMixin):
    def __init__(
        self,
        shopping_cart_items_repository: ShoppingCartItemRepository,
        cart_repository: ShoppingCartRepository,
        service_repository: ServiceRepository,
        service_configs_repository: ServiceConfigsRepository,
        promo_code_repository: PromoCodeRepository
    ):
        self.shopping_cart_items_repository = shopping_cart_items_repository
        super().__init__(cart_repository, shopping_cart_items_repository, service_repository, service_configs_repository,
                         promo_code_repository)

    def execute(self, dto: RemoveCartItemDTOInput) -> RemoveCartItemDTOOutput:
        self.shopping_cart_items_repository.delete(dto.cart_item_id, dto.cart_id)
        cart = self.get_shopping_cart_by_id(dto.cart_id)
        total_price, total_old_price = cart.prices

        return RemoveCartItemDTOOutput(
            success=True,
            cart_id=cart.id,
            total_price=total_price,
            total_old_price=total_old_price,
            promo_code=PromoCodeDTO.from_entity(cart.promo) if cart.promo else None
        )
