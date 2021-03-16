import logging
import typing as t
from typing import List

from django.db.models import QuerySet
from pydantic import EmailStr

from core.application.repositories.order import AbstractBoostersRepository
from core.boosters.application.repository import BoostersRepository
from core.boosters.domain.entities import Booster as Booster
from core.bungie.entities import DestinyBungieProfile, DestinyCharacter
from core.bungie.exceptions import DestinyProfileDoesNotExists
from core.bungie.repositories import DestinyBungieCharacterRepository, DestinyBungieProfileRepository
from core.clients.application.exception import ProfileCredentialsNotFound, UserNotFound
from core.clients.application.repository import ClientCredentialsRepository, ClientsRepository
from core.clients.domain.client import Client, ClientCredential
from core.domain.entities.booster import Booster as OldBooster
from core.domain.entities.shopping_cart.exceptions import CharacterDoesNotExists
from core.domain.exceptions import BoosterNotExists, UserIsNotBooster
from core.domain.object_values import ClientId, DiscordId
from core.shopping_cart.domain.types import ShoppingCartId
from orders.orm_models import ORMOrderObjective
from .constants import Membership

from .models import BoosterUser as BoosterUserORM, User, ProfileCredentials as ProfileCredentialsORM
from .orm_models import ORMDestinyBungieCharacter, ORMDestinyBungieProfile

logger = logging.getLogger(__name__)


class DjangoBoostersRepository(AbstractBoostersRepository):
    def get_by_discord(self, discord_id: DiscordId):
        try:
            booster = BoosterUserORM.objects.get(
                discord_id=discord_id
            )
        except BoosterUserORM.DoesNotExist:
            raise BoosterNotExists()
        return self._encode_booster(booster)

    @staticmethod
    def _encode_booster(booster: BoosterUserORM):
        return OldBooster(
            discord_id=booster.discord_id,
            _id=booster.id,
            user_id=booster.user.first().id,
            username=booster.in_game_profile.username
        )


class DjangoClientRepository(ClientsRepository):
    def list_by_ids(self, client_ids: t.List[int]) -> t.List[Client]:
        users = User.objects.filter(id__in=client_ids)
        return list(map(self.encode_client, users))

    def get_by_id(self, client_id: int) -> Client:
        try:
            user = User.objects.get(id=client_id)
            return self.encode_client(user)
        except User.DoesNotExist:
            raise UserNotFound()

    def save(self, client: Client):
        User.objects.filter(id=client.id).update(
            discord=client.discord,
            cashback=client.cashback,
            last_chat_message_send_at=client.last_chat_message_send_at
        )

    def get_or_create_by_email(self, email: EmailStr) -> Client:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            random_password = User.objects.make_random_password()
            user = User.objects.create_user(
                email=email, username=email, password=random_password
            )
        return self.encode_client(user)

    @staticmethod
    def encode_client(user: User) -> Client:
        username = 'No Username'

        try:
            bungie_profile = user.destiny_profiles.first()
            if bungie_profile:
                username = bungie_profile.username
        except Exception as e:
            logger.exception(e, extra={'user': user})

        return Client(
            _id=user.id,
            email=user.email,
            discord=user.discord,
            username=username,
            cashback=user.cashback,
            avatar=user.booster_profile.avatar.url if user.booster_profile is not None else None,
            last_chat_message_send_at=user.last_chat_message_send_at
        )


class DjangoDestinyBungieProfileRepository(DestinyBungieProfileRepository):
    @staticmethod
    def _encode_profile(profile: ORMDestinyBungieProfile):
        return DestinyBungieProfile(
           membership_id=profile.membership_id,
           membership_type=profile.membership,
           username=profile.username
        )

    def list_by_client_order_id(self, client_order_id: str) -> List[DestinyBungieProfile]:
        profiles = ORMDestinyBungieProfile.objects.filter(
            ormorderobjective__client_order=client_order_id
        )
        return list(map(self._encode_profile, profiles))

    def get_by_id(self, membership_id: str) -> DestinyBungieProfile:
        profile = ORMDestinyBungieProfile.objects.filter(membership_id=membership_id).first()
        if not profile:
            raise DestinyProfileDoesNotExists()
        return self._encode_profile(profile)

    def create_or_update(self, profile: DestinyBungieProfile):
        _, is_created = ORMDestinyBungieProfile.objects.update_or_create(
            membership_id=profile.membership_id,
            membership_type=profile.membership_type.value,
            username=profile.username,
        )

    def get_by_cart_id(self, cart_id: ShoppingCartId):
        profiles = ORMDestinyBungieProfile.objects.prefetch_related('cart_items').filter(
            cart_items__shopping_cart_id=cart_id
        )
        return list(map(self._encode_profile, profiles))

    def list_by_client(self, client_id: int) -> t.List[DestinyBungieProfile]:
        profiles = ORMDestinyBungieProfile.objects.filter(
            client_id=client_id
        )
        return list(map(self._encode_profile, profiles))

    def list_by_orders(self, order_ids: t.List[str]) -> t.List[DestinyBungieProfile]:
        profiles = ORMDestinyBungieProfile.objects.filter(
            ormorderobjective__client_order_id__in=order_ids
        )
        return list(map(self._encode_profile, profiles))

    def bulk_link_with_client_id(self, client_id: int, bungie_profile_ids: t.List[str]) -> t.NoReturn:
        ORMDestinyBungieProfile.objects.filter(
            membership_id__in=bungie_profile_ids,
            client_id=None
        ).update(
            client_id=client_id
        )


class DjangoDestinyCharacterRepository(DestinyBungieCharacterRepository):
    def list_by_orders(self, order_ids: t.List[str]) -> t.List[DestinyCharacter]:
        characters = ORMDestinyBungieCharacter.objects.filter(
            ormorderobjective__client_order_id__in=order_ids
        )
        return list(map(self._encode_model, characters))

    def list_by_client(self, client_id: int) -> t.List[DestinyCharacter]:
        characters = ORMDestinyBungieCharacter.objects.filter(
            bungie_profile__client_id=client_id
        )
        return list(map(self._encode_model, characters))

    @staticmethod
    def _encode_model(character: ORMDestinyBungieCharacter):
        return DestinyCharacter(
            character_id=character.character_id,
            character_class=character.game_class,
            bungie_id=character.bungie_profile.pk
        )

    def get_by_id(self, character_id: str) -> DestinyCharacter:
        character = ORMDestinyBungieCharacter.objects.filter(character_id=character_id).first()
        if not character:
            raise CharacterDoesNotExists()
        else:
            return self._encode_model(character)

    def list_by_client_order_id(self, client_order_id: str) -> t.List[DestinyCharacter]:
        characters = ORMDestinyBungieCharacter.objects.filter(
            ormorderobjective__client_order=client_order_id
        )
        return list(map(self._encode_model, characters))

    def create_or_update(self, character: DestinyCharacter):
        ORMDestinyBungieCharacter.objects.update_or_create(
            bungie_profile_id=character.bungie_id,
            character_id=character.character_id,
            character_class=character.character_class.value
        )


class DjangoProfileCredentialsRepository(ClientCredentialsRepository):
    def list_by_booster_and_orders(
        self,
        booster_id: int,
        client_order_ids: t.List[str]
    ) -> t.List[ClientCredential]:

        orders = ORMOrderObjective.objects.select_related('client_order__platform', 'client_order').filter(
            booster__user__id=booster_id,
        )

        client_ids = set(o.client_order.client_id for o in orders)
        platforms = set(o.client_order.platform.value for o in orders)

        credentials = ProfileCredentialsORM.objects.filter(
            platform__in=platforms,
            owner_id__in=client_ids
        )

        return list(map(self._encode_model, credentials))

    def save(self, credentials: ClientCredential):
        ProfileCredentialsORM.objects.update_or_create(
            defaults=dict(
                account_name=credentials.account_name,
                account_password=credentials.account_password,
                is_expired=credentials.is_expired,
                has_second_factor=credentials.has_second_factor
            ),
            owner_id=credentials.owner_id,
            platform_id=credentials.platform.value,
        )

    @staticmethod
    def _encode_model(
        data: ProfileCredentialsORM
    ):
        return ClientCredential(
            account_name=data.account_name,
            account_password=data.account_password,
            platform=Membership(data.platform.value),
            owner_id=data.owner.pk,
            is_expired=data.is_expired,
            has_second_factor=data.has_second_factor
        )

    def get_by_user_id_and_platform(self, platform: Membership, user_id: int):
        try:
            return self._encode_model(ProfileCredentialsORM.objects.get(platform__value=platform.value, owner_id=user_id))
        except ProfileCredentialsORM.DoesNotExist:
            raise ProfileCredentialsNotFound()

    def list_by_user(self, user_id: int) -> t.List[ClientCredential]:
        res = ProfileCredentialsORM.objects.filter(
            owner_id=user_id
        )
        return list(map(self._encode_model, res))


class DjangoDestinyBoostersRepository(BoostersRepository):

    @staticmethod
    def base_query() -> QuerySet:
        return BoosterUserORM.objects.select_related('in_game_profile')

    def get_by_user_id(self, user_id: int) -> Booster:
        try:
            user = User.objects.get(id=user_id)
            if user.booster_profile and user.is_booster:
                return self._encode(user.booster_profile)
            else:
                raise UserIsNotBooster()
        except User.DoesNotExist:
            raise BoosterNotExists()

    def list_by_client_orders(self, client_id: ClientId) -> t.List[Booster]:
        boosters = (
            self.base_query()
            .filter(ormorderobjective__client_order__client_id=client_id)
            .distinct()
        )
        return list(map(self._encode, boosters))

    @staticmethod
    def _encode(data: BoosterUserORM) -> Booster:
        user = data.user.first()
        return Booster(
            _id=data.id,
            username=data.in_game_profile.username,
            rating=data.rating,
            avatar=data.avatar.url if data.avatar else None,
            user_id=user.id if user else None
        )
