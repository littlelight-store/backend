import logging
import typing as t
from decimal import Decimal

from pydantic import BaseModel, EmailStr

from core.application.repositories.services import ServiceConfigsRepository, ServiceRepository
from core.bungie.repositories import DestinyBungieProfileRepository
from core.clients.application.repository import ClientCredentialsRepository, ClientsRepository
from core.clients.domain.client import Client
from core.clients.application.exception import ProfileCredentialsNotFound
from core.clients.domain.exceptions import NotEnoughCashback
from core.order.application.repository import ClientOrderRepository, MQEventsRepository, OrderObjectiveRepository
from core.order.domain.order import ClientOrder, ClientOrderObjective
from core.shopping_cart.application.repository import (
    PromoCodeRepository, ShoppingCartItemRepository,
    ShoppingCartRepository,
)
from core.shopping_cart.application.use_cases.list_cart_items_mixin import ListCartItemsUseCaseMixin
from core.shopping_cart.domain.shopping_cart import ShoppingCartItem
from profiles.constants import Membership

logger = logging.getLogger(__name__)


class CartPayedDTORequest(BaseModel):
    cart_id: str
    payment_id: str
    user_email: EmailStr
    user_discord: t.Optional[str]
    comment: t.Optional[str]
    pay_with_cashback: Decimal


class CartPayedDTOResponse(BaseModel):
    client_order_id: str
    client_id: int
    success: bool
    should_set_credentials: bool


class CartPayedUseCase(ListCartItemsUseCaseMixin):
    def __init__(
        self,
        cart_repository: ShoppingCartRepository,
        cart_item_repository: ShoppingCartItemRepository,
        order_repository: ClientOrderRepository,
        order_objective_repository: OrderObjectiveRepository,
        clients_repository: ClientsRepository,
        service_repository: ServiceRepository,
        service_configs_repository: ServiceConfigsRepository,
        promo_code_repository: PromoCodeRepository,
        profile_credentials_repository: ClientCredentialsRepository,
        destiny_bungie_profile_repository: DestinyBungieProfileRepository,
        events_repository: MQEventsRepository
    ):
        self.events_repository = events_repository
        self.order_objective_repository = order_objective_repository
        self.service_repository = service_repository
        self.cart_item_repository = cart_item_repository
        self.clients_repository = clients_repository
        self.order_repository = order_repository
        self.cart_repository = cart_repository
        self.service_configs_repository = service_configs_repository
        self.profile_credentials_repository = profile_credentials_repository
        self.destiny_bungie_profile_repository = destiny_bungie_profile_repository

        super().__init__(
            cart_repository,
            cart_item_repository,
            service_repository,
            service_configs_repository,
            promo_code_repository
        )

    def update_game_profiles_with_created_user(
        self,
        client_id: int,
        bungie_profile_ids: t.Iterable[str],
    ):

        self.destiny_bungie_profile_repository.bulk_link_with_client_id(client_id, bungie_profile_ids)

    def execute(self, dto: CartPayedDTORequest) -> CartPayedDTOResponse:
        cart = self.get_shopping_cart_by_id(dto.cart_id)

        client = self.clients_repository.get_or_create_by_email(dto.user_email.lower())
        client.discord = dto.user_discord

        if not client.has_enough_cashback(dto.pay_with_cashback):
            raise NotEnoughCashback()

        profiles = self.destiny_bungie_profile_repository.get_by_cart_id(cart.id)
        platforms = set(p.membership_type for p in profiles)
        if len(platforms) > 1:
            logger.exception('Found more than 1 membership type in cart')
        platform = platforms.pop()

        client_order = ClientOrder.create(
            order_id=cart.id,
            client_id=client.id,
            payment_id=dto.payment_id,
            comment=dto.comment,
            platform=platform,
            promo_code=cart.promo_id,
        )

        profile_ids = set()

        for cart_item in cart.items:  # type: ShoppingCartItem
            profile_ids.add(cart_item.bungie_profile_id)

            objective = ClientOrderObjective.create(
                client_order_id=client_order.id,
                service_slug=cart_item.service_slug,

                destiny_profile_id=cart_item.bungie_profile_id,
                destiny_character_id=cart_item.character_id,

                price=cart_item.price,
                selected_option_ids=[c.id for c in cart_item.selected_options],
                range_options=cart_item.range_options,
                client_id=client.id
            )

            client_order.add_client_order_objective(objective)

        client_order.apply_cashback(dto.pay_with_cashback)
        client.subtract_cashback(dto.pay_with_cashback)
        client.add_cashback(client_order.total_price, percent=5)

        self.update_game_profiles_with_created_user(
            client.id, profile_ids
        )
        self.order_repository.create(order=client_order)
        self.order_objective_repository.create_bulk(client_order.objectives)
        self.clients_repository.save(client)

        self.cart_repository.delete(cart.id)
        self.cart_item_repository.delete_by_shopping_cart(cart.id)
        self.clients_repository.save(client)

        # TODO: Зашедулить таску на отправку данных на почту/в телегу/и т.д.
        self.events_repository.new_order_created(client_order.id)

        return CartPayedDTOResponse(
            success=True,
            client_id=client.id,
            client_order_id=client_order.id,
            should_set_credentials=self.should_set_credentials(platform, client)
        )

    def should_set_credentials(self, platform: Membership, client: Client) -> bool:
        try:
            self.profile_credentials_repository.get_by_user_id_and_platform(str(platform.value), client.id)
            return False
        except ProfileCredentialsNotFound:
            return True
