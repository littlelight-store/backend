import typing as t
from decimal import Decimal

from core.domain.entities.interfaces import IOrder, IService
from orders.enum import OrderStatus
from profiles.constants import Membership
from .booster import Booster
from .bungie_profile import DestinyCharacter, BungieProfile
from .client import Client, GameCredentials
from ..object_values import PaymentId, InvoiceId, ParentOrderId, BoosterId
from ...shopping_cart.domain.promo_code import PromoCode


class ParentOrder:
    def __init__(
        self,
        parent_order_id: t.Optional[ParentOrderId],
        total_price: Decimal,
        invoice_number: InvoiceId,
        payment_id: PaymentId,
        platform: Membership,
        bungie_profile: 'BungieProfile',
        credentials: GameCredentials,
        raw_data: t.Dict[str, t.Any],
        promo: t.Optional[PromoCode],
        comment: str,
        orders: t.List['Order'] = None,
    ):
        if not orders:
            orders = []

        self.payment_id = payment_id
        self.platform = platform
        self.credentials = credentials
        self.invoice_number = invoice_number
        self.total_price = total_price
        self.id = parent_order_id
        self.orders = orders
        self.raw_data = raw_data
        self.bungie_profile = bungie_profile
        self.promo = promo
        self.comment = comment

    @classmethod
    def create(
        cls,
        total_price: Decimal,
        invoice_number: InvoiceId,
        payment_id: PaymentId,
        platform: Membership,
        credentials: GameCredentials,
        bungie_profile: 'BungieProfile',
        promo: t.Optional[PromoCode],
        comment: str,
        raw_data: t.Dict[str, t.Any]
    ):
        return cls(
            total_price=total_price,
            invoice_number=invoice_number,
            payment_id=payment_id,
            platform=platform,
            credentials=credentials,
            raw_data=raw_data,
            promo=promo,
            bungie_profile=bungie_profile,
            comment=comment,
            parent_order_id=None
        )


class Order(IOrder):
    def __init__(
        self,
        service: IService,
        parent_order_id: ParentOrderId,
        booster_price: Decimal,
        total_price: Decimal,
        character: DestinyCharacter,
        status: OrderStatus = OrderStatus.is_checking_payment,
        booster_user_id: t.Optional[BoosterId] = None,
        _id: t.Optional[int] = None
    ):
        self.service = service
        self.parent_order_id = parent_order_id
        self.booster_price = booster_price
        self.total_price = total_price
        self.character = character
        self.status = status
        self.id = _id
        self.booster_user_id = booster_user_id

    def set_booster(self, booster: Booster):
        self.status = OrderStatus.waiting_for_booster
        self.booster_user_id = booster.user_id

    @classmethod
    def create(
        cls,
        service: IService,
        parent_order: 'ParentOrder',
        booster_price: Decimal,
        character: DestinyCharacter,
        total_price: Decimal,
    ):
        return cls(
            service=service,
            parent_order_id=parent_order.id,
            booster_price=booster_price,
            total_price=total_price,
            character=character
        )


class PromoCode:
    def __init__(
        self,
        code: str,
        services: t.List[IService],
        comment: str,
        usage_limit: int,
        first_buy_only: bool,
        discount: int,
    ):
        self.code = code
        self.services = services
        self.comment = comment
        self.usage_limit = usage_limit
        self.first_buy_only = first_buy_only
        self.discount = Decimal(discount)

    def calculate_price(self, service: IService, price: Decimal) -> Decimal:
        if service.slug in [s.slug for s in self.services]:
            discount = price * (self.discount / 100)
            return Decimal(price - discount)
        return price


class Cart:
    services: t.Dict[str, 'IService']

    def __init__(
        self,
        cart_items: t.List['CartItem'],
        payment_id: PaymentId,
        invoice_number: InvoiceId,
        services: t.List['IService'],
        client: Client,
        promo_code: t.Optional[PromoCode] = None
    ):
        """

        @type invoice_number: InvoiceId invoice number from paypal
        """
        self.services = self._map_services(services)
        self.client = client
        self.invoice_number = invoice_number
        self.payment_id = payment_id
        self.cart_items = cart_items
        self.promo_code = promo_code

    @staticmethod
    def create(
        payment_id: PaymentId, invoice_number: InvoiceId, client: Client,
        services: t.List['IService'], promo_code: t.Optional[PromoCode]
    ):
        return Cart(
            payment_id=payment_id,
            invoice_number=invoice_number,
            client=client,
            cart_items=[],
            services=services,
            promo_code=promo_code
        )

    @staticmethod
    def _map_services(services: t.List['IService']):
        data = {}
        for service in services:
            data[service.slug] = service
        return data

    def get_service(self, service_id: str) -> 'IService':
        return self.services[service_id]

    def add_cart_item(self, service, character):
        self.cart_items.append(CartItem.create(
            service=service,
            character=character,
            promo_code=self.promo_code
        ))

    @property
    def total_price(self):
        res = 0
        for item in self.cart_items:
            res += item.total_price
        return res


class CartItem:
    def __init__(
        self,
        service: IService,
        character: DestinyCharacter,
        promo_code: PromoCode
    ):
        self.character = character
        self.service = service
        self.promo_code = promo_code

    @staticmethod
    def create(
        service: IService,
        character: DestinyCharacter,
        promo_code: PromoCode
    ):
        return CartItem(
            service=service,
            character=character,
            promo_code=promo_code
        )

    def _calculate_default_booster_price(self, price: Decimal):
        discount = price * (Decimal(self.service.booster_percent) / 100)
        return Decimal(price - discount)

    @property
    def total_price(self) -> Decimal:
        price = self.service.price
        if self.promo_code:
            price = self.promo_code.calculate_price(self.service, price)
        return price

    @property
    def booster_price(self) -> Decimal:
        res = self._calculate_default_booster_price(self.total_price)
        return res
