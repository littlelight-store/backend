import typing as t

from core.application.repositories import AbstractOrderRepo
from core.domain.entities.bungie_profile import BungieProfile, BungieProfileDTO, DestinyCharacter, DestinyCharacterClass
from core.domain.entities.client import Client, GameCredentials
from core.domain.entities.interfaces import IBooster, IClient
from core.domain.entities.order import Order, ParentOrder, PromoCode
from core.domain.entities.service import Service, ServiceConfig
from core.domain.exceptions import PromoNotFoundException, OrderNotExists
from core.domain.object_values import PromoCodeId
from orders.enum import OrderStatus
from orders.models import Order as OrderORM, ParentOrder as ParentOrderORM
from profiles.models import (
    BungieID, ProfileCredentials as ProfileCredentialsORM, User,
    UserCharacter as UserCharacterORM,
)
from services.models import (
    PromoCode as PromoCodeORM, Service as ServiceORM, ServiceConfig as ServiceConfigORM,
)


class DjangoOrderRepository(AbstractOrderRepo):
    def update_order(self, order: Order) -> t.NoReturn:
        try:
            order_orm = OrderORM.objects.get(id=order.id)
            order_orm.status = order.status.value
            order_orm.booster_user_id = order.booster_user_id
            order_orm.save()
        except OrderORM.DoesNotExist:
            raise OrderNotExists()

    def create_order(self, data: Order, parent_order: ParentOrder) -> Order:
        order = OrderORM.objects.create(
            parent_order_id=data.parent_order_id,
            service_id=data.service.slug,
            bungie_profile_id=parent_order.bungie_profile.id,
            character_id=data.character.id,
            payment_id=parent_order.payment_id,
            invoice_number=parent_order.invoice_number,
            promo_id=parent_order.promo.code if parent_order.promo else None,
            booster_price=data.booster_price,
            total_price=data.total_price,
            raw_data=parent_order.raw_data,
            layout_options=data.service.layout_options,
            comment=parent_order.comment,
            site_id=1
        )
        order.service_config.set([service_config for service_config in data.service.options_ids])
        return self._encode_order(order)

    def _encode_order(
        self,
        order: OrderORM,
    ) -> Order:
        return Order(
            service=self._encode_service(order.service),
            parent_order_id=order.parent_order_id,
            booster_price=order.booster_price,
            total_price=order.total_price,
            character=self._encode_character(order.character),
            status=OrderStatus(order.status),
            _id=order.id
        )

    def get_credentials(self, bungie_profile: BungieProfile) -> t.Optional[GameCredentials]:
        try:
            credentials = ProfileCredentialsORM.objects.get(
                owner_id=bungie_profile.owner_id,
                platform__value=bungie_profile.membership_type.value
            )
            return self._encode_credentials(credentials)
        except ProfileCredentialsORM.DoesNotExist:
            return None

    def get_options(self, options_id: str) -> t.List[ServiceConfig]:
        orm_configs = ServiceConfigORM.objects.filter(id__in=options_id)
        return [self._encode_service_config(c) for c in orm_configs]

    def get_or_create_character(
        self, bungie_profile: BungieProfile, character_id: str,
        character_class: DestinyCharacterClass
    ) -> DestinyCharacter:
        character, _ = UserCharacterORM.objects.get_or_create(
            bungie_profile_id=bungie_profile.id,
            character_id=character_id,
            defaults=dict(
                character_class=character_class.value
            )
        )
        return self._encode_character(character)

    def get_or_create_bungie_id(
        self,
        bungie_profile_data: BungieProfileDTO,
        user: t.Union[IClient, IBooster]
    ) -> BungieProfile:
        bungie_profile, _ = BungieID.objects.get_or_create(
            owner_id=user.client_id,
            membership_id=bungie_profile_data.membership_id,
            membership_type=bungie_profile_data.membership_type.value,
            defaults=dict(
                username=bungie_profile_data.username,
            ),
        )
        return self._encode_bungie_profile(bungie_profile, user)

    def get_or_create_client(self, user_email) -> Client:
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            random_password = User.objects.make_random_password()
            user = User.objects.create_user(
                email=user_email, username=user_email, password=random_password
            )
        return self.encode_client(user)

    @staticmethod
    def _encode_bungie_profile(profile: BungieID, user: t.Union[IClient, IBooster]) -> BungieProfile:
        return BungieProfile(
            username=profile.username,
            owner=user,
            membership_id=profile.membership_id,
            membership_type=profile.membership_type,
            owner_id=profile.owner.id,
            _id=profile.id
        )

    @staticmethod
    def encode_client(user: User) -> Client:
        return Client(
            email=user.email,
            client_id=user.id
        )

    @staticmethod
    def _encode_character(character: UserCharacterORM) -> DestinyCharacter:
        return DestinyCharacter(
            id=character.id,
            characterId=character.character_id,
            classType=int(character.character_class),
        )

    @staticmethod
    def _encode_service(service: ServiceORM) -> Service:
        return Service(
            title=service.title,
            slug=service.slug,
            booster_percent=service.booster_price,
            layout_type=service.option_type,
            category=service.category.slug
        )

    @staticmethod
    def _encode_service_config(service_config: ServiceConfigORM) -> ServiceConfig:
        return ServiceConfig(
            title=service_config.title,
            _id=service_config.id,
            description=service_config.description,
            price=service_config.price,
            old_price=service_config.old_price,
            extra_data=service_config.extra_configs
        )

    @staticmethod
    def _encode_promo(promo: PromoCodeORM) -> PromoCode:
        return PromoCode(
            code=promo.code,
            services=[DjangoOrderRepository._encode_service(service) for service in promo.service.all()],
            comment=promo.comment,
            usage_limit=promo.usage_limit,
            first_buy_only=promo.first_buy_only,
            discount=promo.discount,
        )

    @staticmethod
    def _encode_credentials(credentials: ProfileCredentialsORM) -> GameCredentials:
        return GameCredentials(
            name=credentials.account_name,
            password=credentials.account_password,
            platform=credentials.platform.value,
            credentials_id=credentials.id
        )

    def get_promo_code(self, pk: PromoCodeId) -> PromoCode:
        try:
            promo = PromoCodeORM.objects.prefetch_related('service').get(pk=pk)
        except PromoCodeORM.DoesNotExist:
            raise PromoNotFoundException()
        else:
            return self._encode_promo(promo)

    def get_services(self, slugs: t.List[str]) -> t.List[Service]:
        services = ServiceORM.objects.filter(slug__in=slugs)
        return [self._encode_service(service) for service in services]

    def create_parent_order(self, data: ParentOrder):
        order = ParentOrderORM.objects.create(
            total_price=data.total_price,
            invoice_number=data.invoice_number,
            payment_id=data.payment_id,
            credentials_id=data.credentials.id if data.credentials else None,
            platform_id=data.platform.value,
            raw_data={},
            site_id=1
        )
        data.id = order.id
        return data

    def get_order(self, order_id: int) -> Order:
        try:
            order = OrderORM.objects.get(id=order_id)
        except OrderORM.DoesNotExist:
            raise OrderNotExists()
        return self._encode_order(order)
