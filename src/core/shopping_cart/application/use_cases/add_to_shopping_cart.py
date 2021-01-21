import logging
import typing as t

from pydantic import BaseModel

from core.application.repositories.services import ServiceConfigsRepository, ServiceRepository
from core.bungie.entities import DestinyBungieProfile, DestinyCharacter
from core.bungie.repositories import DestinyBungieCharacterRepository, DestinyBungieProfileRepository
from core.domain.entities.shopping_cart.exceptions import ShoppingCartDoesNotExists
from core.shopping_cart.application.repository import (
    PromoCodeRepository, ShoppingCartItemRepository,
    ShoppingCartRepository,
)
from core.shopping_cart.application.use_cases.dto import CartRangeOptionsDTO, CartResponse, PromoCodeDTO
from core.shopping_cart.application.use_cases.list_cart_items_mixin import ListCartItemsUseCaseMixin
from core.shopping_cart.domain.shopping_cart import ShoppingCart, ShoppingCartItem
from core.shopping_cart.domain.types import ShoppingCartId
from profiles.constants import CharacterClasses, Membership

logger = logging.getLogger(__name__)


class BungieProfileDTO(BaseModel):
    membership_id: str
    membership_type: Membership
    username: str


class BungieDestinyCharacterDTO(BaseModel):
    character_id: str
    character_class: CharacterClasses
    bungie_profile_id: str


class ItemAddedToCart(BaseModel):
    bungie_profile: BungieProfileDTO
    character: BungieDestinyCharacterDTO
    option_ids: t.List[int]
    service_slug: str
    range_options: t.Optional[CartRangeOptionsDTO]


class AddItemToShoppingCartDTOInput(BaseModel):
    cart_id: t.Optional[ShoppingCartId]
    adding_to_cart: ItemAddedToCart


class AddItemToShoppingCartDTOOutput(CartResponse):
    cart_item_id: str
    added: bool


class AddItemToShoppingCartUseCase(ListCartItemsUseCaseMixin):

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
        self.destiny_bungie_profile_repository = destiny_bungie_profile_repository
        self.destiny_character_repository = destiny_character_repository
        self.shopping_cart_items_repository = shopping_cart_items_repository
        self.shopping_cart_repository = shopping_cart_repository

        super().__init__(
            shopping_cart_repository,
            shopping_cart_items_repository,
            service_repository,
            service_configs_repository,
            promo_code_repository
        )

    def _get_or_create_cart(
        self,
        cart_id: t.Optional[str],
    ) -> ShoppingCart:

        try:
            if not cart_id:
                raise ShoppingCartDoesNotExists()

            cart = self.get_shopping_cart_by_id(cart_id)
        except ShoppingCartDoesNotExists:
            cart = ShoppingCart.create()

        return cart

    def _update_bungie_entities(
        self,
        bungie_profile: BungieProfileDTO,
        destiny_character: BungieDestinyCharacterDTO
    ) -> t.Tuple[DestinyBungieProfile, DestinyCharacter]:
        destiny_bungie_profile = DestinyBungieProfile(
            membership_id=bungie_profile.membership_id,
            username=bungie_profile.username,
            membership_type=bungie_profile.membership_type
        )

        destiny_bungie_character = DestinyCharacter(
            character_id=destiny_character.character_id,
            character_class=destiny_character.character_class,
            bungie_id=destiny_character.bungie_profile_id
        )

        self.destiny_bungie_profile_repository.create_or_update(destiny_bungie_profile)
        self.destiny_character_repository.create_or_update(destiny_bungie_character)

        return destiny_bungie_profile, destiny_bungie_character

    def execute(self, dto: AddItemToShoppingCartDTOInput) -> AddItemToShoppingCartDTOOutput:
        logger.info(f'Adding item to cart with: {dto}')

        cart = self._get_or_create_cart(dto.cart_id)

        bungie_profile, destiny_character = self._update_bungie_entities(
            dto.adding_to_cart.bungie_profile,
            dto.adding_to_cart.character
        )

        cart_item = ShoppingCartItem.create(
            bungie_profile_id=bungie_profile.id,
            character_id=destiny_character.id,
            service_slug=dto.adding_to_cart.service_slug,
            shopping_cart_id=cart.id,
            range_options=dto.adding_to_cart.range_options.dict() if dto.adding_to_cart.range_options else None
        )

        service_config_option_ids = dto.adding_to_cart.option_ids

        self.shopping_cart_repository.create(cart)
        self.shopping_cart_items_repository.create(
            cart_item,
            service_config_option_ids,
        )

        self.calculate_price_for_cart_item(cart_item)
        cart.add_item(cart_item)
        total_price, total_old_price = cart.prices
        return AddItemToShoppingCartDTOOutput(
            cart_id=cart.id,
            cart_item_id=cart_item.id,
            added=True,
            total_price=total_price,
            total_old_price=total_old_price,
            promo_code=PromoCodeDTO.from_entity(
                cart.promo
            ) if cart.promo else None

        )
