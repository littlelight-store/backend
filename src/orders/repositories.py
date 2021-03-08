import logging
import typing as t

from django.db.models import Q

from core.chat.domain.chat_room import ChatMessage, ChatRole, ChatRoom
from core.chat.application.repository import ChatMessagesRepository, ChatRoomRepository
from core.domain.entities.shopping_cart.exceptions import ShoppingCartDoesNotExists
from core.order.application.exceptions import OrderDoesNotExists, OrderObjectiveNotExists
from core.order.application.repository import OrderObjectiveRepository, ClientOrderRepository
from core.order.domain.order import ClientOrder, ClientOrderObjective
from core.shopping_cart.application.repository import (
    PromoCodeRepository, ShoppingCartItemRepository,
    ShoppingCartRepository,
)
from core.shopping_cart.domain.promo_code import PromoCode, PromoCodeDoesNotExists
from core.shopping_cart.domain.shopping_cart import ShoppingCart, ShoppingCartItem
from core.shopping_cart.domain.types import ShoppingCartId
from orders.orm_models import (
    ChatMessage as ORMChatMessage, ORMClientOrder, ORMOrderObjective, ORMShoppingCart,
    ORMShoppingCartItem,
)
from profiles.constants import Membership
from services.models import ServiceConfig, PromoCode as ORMPromoCode

logger = logging.getLogger(__name__)


class DjangoShoppingCartRepository(ShoppingCartRepository):

    @staticmethod
    def _encode_shopping_cart(data: ORMShoppingCart):
        return ShoppingCart(
            _id=data.id,
            created_at=data.created_at,
            promo_id=data.promo_code_id
        )

    def get_by_id(self, shopping_cart_id: str) -> ShoppingCart:
        res = ORMShoppingCart.objects.filter(id=shopping_cart_id).first()

        if not res:
            raise ShoppingCartDoesNotExists()

        return self._encode_shopping_cart(res)

    def create(self, shopping_cart: ShoppingCart) -> t.NoReturn:
        ORMShoppingCart.objects.update_or_create(
            id=shopping_cart.id,
            created_at=shopping_cart.created_at,
        )

    def update(self, shopping_cart: ShoppingCart) -> t.NoReturn:
        ORMShoppingCart.objects.filter(
            id=shopping_cart.id,
        ).update(
            promo_code_id=shopping_cart.promo_id
        )

    def delete(self, shopping_cart_id: str):
        ORMShoppingCart.objects.filter(id=shopping_cart_id).delete()


class DjangoShoppingCartItemRepository(ShoppingCartItemRepository):

    def delete_by_shopping_cart(self, shopping_cart_id: ShoppingCartId):
        ORMShoppingCartItem.objects.filter(shopping_cart_id=shopping_cart_id).delete()

    def delete(self, cart_item_id: str, shopping_cart_id: str):
        ORMShoppingCartItem.objects.filter(shopping_cart_id=shopping_cart_id, id=cart_item_id).delete()

    @staticmethod
    def _encode_model(data: ORMShoppingCartItem) -> ShoppingCartItem:
        return ShoppingCartItem(
            bungie_profile_id=data.bungie_profile.membership_id,
            character_id=data.character.character_id,
            _id=data.id,
            shopping_cart_id=data.shopping_cart.id,
            service_slug=data.service.slug,
            range_options=data.range_options,
        )

    def create(
        self, item: ShoppingCartItem, options: t.List[int],
    ) -> ShoppingCartItem:
        cart_item = ORMShoppingCartItem.objects.create(
            bungie_profile_id=item.bungie_profile_id,
            character_id=item.character_id,
            id=item.id,
            service_id=item.service_slug,
            shopping_cart_id=item.shopping_cart_id,
            range_options=item.range_options
        )

        cart_item.selected_options.set(options)

        return self._encode_model(cart_item)

    def get_by_shopping_cart(self, shopping_cart: ShoppingCart) -> t.List[ShoppingCartItem]:
        items = ORMShoppingCartItem.objects.filter(shopping_cart=shopping_cart.id)
        return list(map(self._encode_model, items))


class DjangoClientOrderRepository(ClientOrderRepository):
    def get_by_order_objective(
        self,
        order_objective_id: str
    ) -> ClientOrder:
        order = ORMClientOrder.objects.get(
            ormorderobjective__id=order_objective_id
        )
        return self._encode(order)

    def save(self, client_order: ClientOrder):
        ORMClientOrder.objects.filter(
            id=client_order.id
        ).update(
            order_status=client_order.order_status,
            order_status_changed_at=client_order.order_status_changed_at
        )

    def get_by_cart_id(self, cart_id: ShoppingCartId) -> ClientOrder:
        order = ORMClientOrder.objects.filter(
            order_id=cart_id
        ).first()
        if not order:
            raise OrderDoesNotExists()
        else:
            return self._encode(order)

    def list_by_user(self, user_id: int) -> t.List[ClientOrder]:
        orders = ORMClientOrder.objects.filter(
            client_id=user_id
        )
        return list(map(self._encode, orders))

    def get_by_id(self, order_id: str) -> ClientOrder:
        try:
            order = ORMClientOrder.objects.get(id=order_id)
            return self._encode(order)
        except ORMClientOrder.DoesNotExist:
            raise OrderDoesNotExists()

    def create(self, order: ClientOrder) -> t.NoReturn:
        logger.info(f'Creating order: {order}')
        ORMClientOrder.objects.create(
            id=order.id,
            total_price=order.total_price,
            order_id=order.order_id,
            client_id=order.client_id,
            payment_id=order.payment_id,
            created_at=order.created_at,
            order_status=order.order_status.name,
            order_status_changed_at=order.order_status_changed_at,
            comment=order.comment,
            platform_id=order.platform,
            promo_id=order.promo_code,
            payed_with_cashback=order.cashback
        )

    @staticmethod
    def _encode(data: ORMClientOrder):
        return ClientOrder(
            total_price=data.total_price,
            created_at=data.created_at,
            comment=data.comment,
            order_id=data.order_id,
            order_status=data.order_status,
            order_status_changed_at=data.order_status_changed_at,
            _id=data.id,
            client_id=data.client_id,
            payment_id=data.payment_id,
            platform=Membership(data.platform.value) if data.platform else None,
            cashback=data.payed_with_cashback
        )


class DjangoOrderObjectiveRepository(OrderObjectiveRepository):

    def list_by_booster(self, booster_id: int) -> t.List[ClientOrderObjective]:
        objs = ORMOrderObjective.objects.filter(
            booster__user__id=booster_id
        )
        return list(map(self._encode, objs))

    def list_by_client(self, client_id: int) -> t.List[ClientOrderObjective]:
        objs = ORMOrderObjective.objects.filter(
            client_order__client__id=client_id
        )
        return list(map(self._encode, objs))

    def get_by_user_and_id(self, order_objective_id: str, client_id: int) -> ClientOrderObjective:
        try:
            objective = ORMOrderObjective.objects.filter(
                Q(client_order__client_id=client_id) | Q(booster__user__id=client_id),
                id=order_objective_id,
            ).first()
            if not objective:
                raise OrderObjectiveNotExists()

            return self._encode(objective)
        except ORMOrderObjective.DoesNotExist:
            raise OrderObjectiveNotExists()

    def save(self, order: ClientOrderObjective):
        ORMOrderObjective.objects.filter(id=order.id).update(
            status=order.status,
            status_changed_at=order.status_changed_at
        )

    def list_by_orders(self, order_ids: t.List[str]):
        objs = ORMOrderObjective.objects.filter(
            client_order_id__in=order_ids
        )
        return list(map(self._encode, objs))

    def get_by_order(self, order_id: str) -> t.List[ClientOrderObjective]:
        objs = ORMOrderObjective.objects.prefetch_related('selected_options').filter(
            client_order=order_id
        )
        return list(map(self._encode, objs))

    @staticmethod
    def _encode(data: ORMOrderObjective):
        return ClientOrderObjective(
            _id=data.id,
            client_order_id=data.client_order_id,
            service_slug=data.service_id,
            destiny_profile_id=data.destiny_profile_id,
            destiny_character_id=data.destiny_character_id,
            selected_option_ids=[c.id for c in data.selected_options.filter()],
            price=data.price,
            range_options=data.range_options,
            status=data.status,
            status_changed_at=data.status_changed_at,
            booster_id=data.booster_id,
            created_at=data.created_at,
            client_id=data.client_order.client_id
        )

    def create_bulk(self, order_objectives: t.List[ClientOrderObjective]):
        for order_objective in order_objectives:
            _orm_obj = ORMOrderObjective(
                id=order_objective.id,
                client_order_id=order_objective.client_order_id,
                service_id=order_objective.service_slug,
                destiny_profile_id=order_objective.destiny_profile_id,
                destiny_character_id=order_objective.destiny_character_id,
                price=order_objective.price,
                status=order_objective.status.name,
                status_changed_at=order_objective.status_changed_at,
                booster_id=order_objective.booster_id,
                created_at=order_objective.created_at
            )
            _orm_obj.save()

            for option in ServiceConfig.objects.filter(id__in=order_objective.selected_option_ids):
                _orm_obj.selected_options.add(option)


class DjangoPromoCodeRepository(PromoCodeRepository):
    @staticmethod
    def _encode_model(data: ORMPromoCode) -> PromoCode:
        return PromoCode(
            code=data.code,
            service_slugs=[s.slug for s in data.service.all()],
            comment=data.comment,
            usage_limit=data.usage_limit,
            first_by_only=data.first_buy_only,
            discount=data.discount
        )

    def find_by_code(self, code: str) -> PromoCode:
        try:
            data = ORMPromoCode.objects.prefetch_related('service').get(
                code=code
            )
            return self._encode_model(data)
        except ORMPromoCode.DoesNotExist:
            raise PromoCodeDoesNotExists()


class DjangoChatRoomRepository(ChatRoomRepository):

    def get_chat_room(
        self,
        user_id: int,
        user_id_2: int,
        role: ChatRole
    ) -> ChatRoom:
        try:
            objective = ORMOrderObjective.objects.filter(
                Q(
                    Q(client_order__client_id=user_id) & Q(booster__user__id=user_id_2),
                ) | Q(
                    Q(client_order__client_id=user_id_2) & Q(booster__user__id=user_id),
                )
            ).first()
            if not objective:
                raise OrderObjectiveNotExists()
            chat_room = self._encode_chat_room(objective)
            return chat_room
        except ORMOrderObjective.DoesNotExist:
            raise OrderObjectiveNotExists()

    def list_rooms_by_user(self, user_id) -> t.List[ChatRoom]:
        messages = ORMOrderObjective.objects.order_by(
            'client_order__client_id',
            'booster__user__id'
        ).distinct(
            'client_order__client_id',
            'booster__user__id'
        ).filter(
            Q(client_order__client_id=user_id) |
            Q(booster__user__id=user_id),
            booster__isnull=False
        )
        return list(map(self._encode_chat_room, messages))

    @staticmethod
    def _encode_chat_room(order_objective: ORMOrderObjective):
        return ChatRoom(
            client_id=order_objective.client_order.client_id,
            booster_id=order_objective.booster.user.first().id,
        )


class DjangoChatMessagesRepository(ChatMessagesRepository):
    def create(self, message: ChatMessage):
        ORMChatMessage.objects.create(
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            msg=message.text,
            created_at=message.created_at
        )

    def list_messages_by_users_pair(self, client_id: int, booster_id: int) -> t.List[ChatMessage]:
        messages = ORMChatMessage.objects.filter(
            (
                Q(sender=client_id) &
                Q(receiver=booster_id)
            ) |
            (
                Q(sender=booster_id) &
                Q(receiver=client_id)
            )
        ).order_by('created_at')
        return list(map(self._encode, messages))

    @staticmethod
    def _encode(message: ORMChatMessage) -> ChatMessage:
        return ChatMessage(
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            created_at=message.created_at,
            text=message.msg,
        )
