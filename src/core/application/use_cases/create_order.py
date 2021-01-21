import typing as t

from pydantic import BaseModel, Field

from core.application.repositories import NotificationsRepository, OrderRepo
from core.application.repositories.order import ReviewRepo
from core.domain.entities.bungie_profile import BungieProfileDTO, DestinyCharacter
from core.domain.entities.order import Cart, ParentOrder, Order
from core.domain.entities.review import Review
from profiles.constants import Membership


class CreateOrderPromoCodeDTO(BaseModel):
    code: str


class OrderCartDataDTO(BaseModel):
    product: t.Dict[str, str] = Field(..., alias='product')
    layout_options: t.Dict[str, t.Any] = Field(..., alias='layoutOptions')
    character_id: str = Field(..., alias='characterId')


class CreateOrderDTO(BaseModel):
    user_email: str
    bungie_profile: BungieProfileDTO
    characters: t.Dict[str, DestinyCharacter]
    discount_object: t.Optional[CreateOrderPromoCodeDTO] = Field(None, alias='discountObject')
    cart_data: t.List[OrderCartDataDTO] = Field(..., alias='cartData')
    payment_id: str = Field(..., alias='paymentId')
    invoice_number: str = Field(..., alias='invoiceNumber')
    comment: str = Field(...)
    platform: Membership = Field(...)


class CreateOrderUseCase:
    order_params: CreateOrderDTO

    def __init__(
        self,
        order_repo: OrderRepo,
        reviews_repo: ReviewRepo,
        notification_repo: NotificationsRepository
    ):
        self.reviews_repo = reviews_repo
        self.notification_repo = notification_repo
        self.order_repo = order_repo

    def set_params(self, order_params: CreateOrderDTO):
        self.order_params = order_params
        return self

    def execute(self):
        client = self.order_repo.get_or_create_client(self.order_params.user_email)
        bungie_profile = self.order_repo.get_or_create_bungie_id(self.order_params.bungie_profile, client)

        promo_code = None

        if self.order_params.discount_object:
            promo_code = self.order_repo.get_promo_code(self.order_params.discount_object.code)

        services = self.order_repo.get_cart_products([
            cart_item.product['slug'] for cart_item in self.order_params.cart_data]
        )

        bungie_profile.set_characters([
            self.order_repo.get_or_create_character(
                bungie_profile,
                character_id=c.character_id,
                character_class=c.character_class
            )
            for c in self.order_params.characters.values()
        ])

        cart = Cart.create(
            invoice_number=self.order_params.invoice_number,
            payment_id=self.order_params.payment_id,
            client=client,
            services=services,
            promo_code=promo_code
        )

        credentials = self.order_repo.get_credentials(
            bungie_profile
        )

        for cart_item in self.order_params.cart_data:
            service = cart.get_service(cart_item.product['slug'])
            service.layout_options = cart_item.layout_options
            service.configs = self.order_repo.get_service_options(service.options_ids)

            character = bungie_profile.get_character(cart_item.character_id)

            cart.add_cart_item(service, character)

        parent_order = ParentOrder.create(
            total_price=cart.total_price,
            invoice_number=cart.invoice_number,
            payment_id=cart.payment_id,
            credentials=credentials,
            platform=bungie_profile.membership_type,
            promo=promo_code,
            bungie_profile=bungie_profile,
            comment=self.order_params.comment,
            raw_data=self.order_params.dict()
        )

        parent_order = self.order_repo.create_parent_order(parent_order)

        orders: t.List[Order] = []
        for cart_item in cart.cart_items:
            order_data = Order.create(
                service=cart_item.service,
                parent_order=parent_order,
                character=cart_item.character,
                booster_price=cart_item.booster_price,
                total_price=cart_item.total_price,
            )

            self.order_repo.create_order(order_data, parent_order)
            orders.append(order_data)

        parent_order.orders = orders

        review = Review.create(client, parent_order)
        self.reviews_repo.create_review(review)

        self.notification_repo.order_created(parent_order, client, with_notification=True)

        result = {
            "user": client.client_id,
            "parent_order": parent_order.id,
            "status": "ok",
            "bungie_id": bungie_profile.id,
        }

        return result
