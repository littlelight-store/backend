import datetime as dt
import typing as t
from decimal import Decimal

from core.domain.entities.service import Service, ServiceConfig
from core.shopping_cart.domain.promo_code import PromoCode
from core.shopping_cart.domain.types import ShoppingCartId
from core.domain.utils import generate_id


class ShoppingCartItem:
    def __init__(
        self,
        _id: str,
        bungie_profile_id: str,
        character_id: str,
        service_slug: str,
        shopping_cart_id: str,
        range_options: t.Optional[dict],
        price: t.Optional[Decimal] = 0,
        old_price: t.Optional[Decimal] = None,
        is_created: bool = True,
        selected_options: t.List[ServiceConfig] = None,
        service: t.Optional[Service] = None,
    ):
        if selected_options is None:
            selected_options = []

        self.range_options = range_options
        self.shopping_cart_id = shopping_cart_id
        self.id = _id
        self.service_slug = service_slug
        self.character_id = character_id
        self.bungie_profile_id = bungie_profile_id
        self.is_created = is_created
        self.price = price
        self.old_price = old_price,
        self.selected_options = selected_options
        self.service = service

    @classmethod
    def create(
        cls,
        bungie_profile_id: str,
        character_id: str,
        service_slug: str,
        shopping_cart_id: str,
        range_options: t.Optional[dict],
    ):
        return cls(
            _id=generate_id(),
            bungie_profile_id=bungie_profile_id,
            character_id=character_id,
            service_slug=service_slug,
            shopping_cart_id=shopping_cart_id,
            range_options=range_options,
            is_created=False,
        )


class ShoppingCart:

    def __init__(
        self,
        _id: ShoppingCartId,
        created_at: dt.datetime,
        price: t.Optional[Decimal] = 0,
        promo_id: t.Optional[str] = None,

        items=None,  # type: t.List[ShoppingCartItem]

        _is_created=True
    ):
        if items is None:
            items = []

        self.price = price

        self.id = _id
        self.items = items
        self.created_at = created_at
        self.is_created = _is_created
        self.promo_id = promo_id

    promo: t.Optional[PromoCode] = None
    items_to_create = []

    def set_current_items(self, items: t.List[ShoppingCartItem]):
        self.items += items

    def add_item(self, item: ShoppingCartItem):
        self.items.append(
            item
        )

    def apply_promo(self, promo: t.Optional[PromoCode]):
        if promo:
            self.promo_id = promo.id
            self.promo = promo
        else:
            self.promo_id = None
            self.promo = None

    @property
    def prices(self) -> t.Tuple[Decimal, Decimal]:
        total_price = total_old_price = Decimal(0)

        for item in self.items:
            if self.promo and self.promo.includes_service(item.service_slug):
                total_price += self.promo.price_discount(item.price)
                total_old_price += item.price
            else:
                total_price += item.price
                total_old_price += item.old_price

        return total_price, total_old_price

    @classmethod
    def create(
        cls,
    ):
        return cls(
            _id=generate_id(),
            created_at=dt.datetime.now(),
            _is_created=False,
        )
