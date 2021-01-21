import typing as t
from decimal import Decimal

from pydantic import BaseModel, Field

from core.domain.entities.bungie_profile import DestinyCharacterClass
from core.domain.entities.constants import ConfigurationType
from core.shopping_cart.domain.promo_code import PromoCode
from core.shopping_cart.domain.types import ShoppingCartId
from profiles.constants import CharacterClasses, Membership


class CartServiceDTO(BaseModel):
    title: str
    slug: str
    base_price: t.Optional[int]
    configuration_type: t.Optional[ConfigurationType]


class CartServiceOptionDTO(BaseModel):
    title: str
    id: int
    description: str
    price: Decimal
    old_price: t.Optional[Decimal]
    extra_data: t.Optional[dict]


class CartDestinyProfileDTO(BaseModel):
    display_name: str
    membership_id: str
    membership_type: Membership


class CartDestinyCharacterDTO(BaseModel):
    character_id: str
    character_class: CharacterClasses
    membership_id: str


class CartRangeOptionsDTO(BaseModel):
    totalPrice: int
    totalOldPrice: int
    firstLabel: str
    lastLabel: str
    pointsFrom: int
    pointsTo: int


class CartItemModel(BaseModel):
    id: str
    service: CartServiceDTO
    options: t.List[CartServiceOptionDTO]
    destiny_profile: CartDestinyProfileDTO
    destiny_character: CartDestinyCharacterDTO
    range_options: t.Optional[CartRangeOptionsDTO]


class PromoCodeDTO(BaseModel):
    comment: t.Optional[str]
    code: str

    @classmethod
    def from_entity(cls, entity: PromoCode):
        return cls(
            code=entity.code,
            comment=entity.comment
        )


class CartResponse(BaseModel):
    total_price: Decimal = Field(0)
    total_old_price: Decimal = Field(0)
    promo_code: t.Optional[PromoCodeDTO]
    cart_id: t.Optional[ShoppingCartId]


class CartObjectiveSelectedOptionsDTO(BaseModel):
    title: str
    price: str


class CartObjectiveDataDTO(BaseModel):
    service_title: str

    character_class: DestinyCharacterClass
    selected_options: t.List[CartObjectiveSelectedOptionsDTO]
    range_configs: t.Optional[t.Dict[str, str]] = None
    promo_id: t.Optional[str] = None
    price: Decimal
