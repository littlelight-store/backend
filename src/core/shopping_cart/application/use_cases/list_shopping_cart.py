import logging
import typing as t
from decimal import Decimal

from pydantic import BaseModel, Field

from core.application.repositories.services import ServiceConfigsRepository, ServiceRepository
from core.shopping_cart.application.repository import (
    PromoCodeRepository, ShoppingCartItemRepository,
    ShoppingCartRepository,
)
from core.shopping_cart.application.use_cases.dto import (
    CartDestinyCharacterDTO, CartDestinyProfileDTO, CartItemModel, CartResponse, CartServiceDTO,
    CartServiceOptionDTO, PromoCodeDTO,
)
from core.bungie.repositories import DestinyBungieCharacterRepository, DestinyBungieProfileRepository
from core.shopping_cart.application.use_cases.list_cart_items_mixin import ListCartItemsUseCaseMixin
from core.shopping_cart.domain.promo_code import PromoCode, PromoCodeDoesNotExists
from core.shopping_cart.domain.shopping_cart import ShoppingCart
from core.shopping_cart.domain.types import ShoppingCartId

logger = logging.getLogger(__name__)


class ListShoppingCartDTOInput(BaseModel):
    cart_id: t.Optional[ShoppingCartId]


class ListShoppingCartDTOOutput(CartResponse):
    cart_items: t.List[CartItemModel]


class ListShoppingCartUseCase(ListCartItemsUseCaseMixin):

    def __init__(
        self,
        shopping_cart_repository: ShoppingCartRepository,
        shopping_cart_items_repository: ShoppingCartItemRepository,
        destiny_bungie_profile_repository: DestinyBungieProfileRepository,
        destiny_character_repository: DestinyBungieCharacterRepository,
        service_repository: ServiceRepository,
        service_configs_repository: ServiceConfigsRepository,
        promo_code_repository: PromoCodeRepository
    ):
        self.promo_code_repository = promo_code_repository
        self.service_configs_repository = service_configs_repository
        self.service_repository = service_repository
        self.destiny_bungie_profile_repository = destiny_bungie_profile_repository
        self.destiny_character_repository = destiny_character_repository
        self.shopping_cart_items_repository = shopping_cart_items_repository
        self.shopping_cart_repository = shopping_cart_repository
        super().__init__(
            cart_repository=shopping_cart_repository,
            cart_item_repository=shopping_cart_items_repository,
            service_repository=service_repository,
            service_configs_repository=service_configs_repository,
            promo_code_repository=promo_code_repository
        )

    def _apply_promo(self, cart: ShoppingCart) -> PromoCode:
        promo_code = None
        if cart.promo_id:
            try:
                promo_code = self.promo_code_repository.find_by_code(cart.promo_id)
                cart.apply_promo(promo_code)
            except PromoCodeDoesNotExists:
                pass
        return promo_code

    def execute(self, dto: ListShoppingCartDTOInput) -> ListShoppingCartDTOOutput:
        cart = self.get_shopping_cart_by_id(dto.cart_id)

        result: t.List[CartItemModel] = []

        for cart_item in cart.items:
            destiny_profile = self.destiny_bungie_profile_repository.get_by_id(cart_item.bungie_profile_id)
            destiny_character = self.destiny_character_repository.get_by_id(cart_item.character_id)

            service = cart_item.service
            selected_options = cart_item.selected_options

            result.append(
                CartItemModel(
                    service=CartServiceDTO(
                        title=service.title,
                        base_price=service.base_price,
                        slug=service.slug,
                        configuration_type=service.configuration_type
                    ),
                    options=[
                        CartServiceOptionDTO(
                            title=o.title,
                            price=o.price,
                            old_price=o.old_price,
                            id=o.id,
                            description=o.description,
                            extra_data=o.extra_data
                        ) for o in selected_options
                    ],
                    destiny_character=CartDestinyCharacterDTO(
                        character_id=destiny_character.character_id,
                        character_class=destiny_character.character_class,
                        membership_id=destiny_character.bungie_id
                    ),
                    destiny_profile=CartDestinyProfileDTO(
                        display_name=destiny_profile.username,
                        membership_id=destiny_profile.membership_id,
                        membership_type=destiny_profile.membership_type
                    ),
                    id=cart_item.id,
                    range_options=cart_item.range_options
                ))

        total_price, total_old_price = cart.prices
        return ListShoppingCartDTOOutput(
            cart_id=cart.id,
            cart_items=result,
            total_price=total_price,
            total_old_price=total_old_price,
            promo_code=PromoCodeDTO.from_entity(
                cart.promo
            ) if cart.promo else None
        )
