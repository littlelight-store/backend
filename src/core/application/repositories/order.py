import abc
import typing as t

from core.domain.entities.bungie_profile import BungieProfileDTO, BungieProfile, DestinyCharacterClass, DestinyCharacter
from core.domain.entities.client import GameCredentials, Client
from core.domain.entities.interfaces import IClient, IBooster
from core.domain.entities.order import ParentOrder, Order, PromoCode
from core.domain.entities.review import Review
from core.domain.entities.service import Service, ServiceConfig
from core.domain.object_values import PromoCodeId, DiscordId, OrderId


class AbstractOrderRepo(abc.ABC):
    @abc.abstractmethod
    def get_or_create_bungie_id(
        self, bungie_profile_data: BungieProfileDTO, user: t.Union[IClient, IBooster]
    ) -> BungieProfile:
        pass

    @abc.abstractmethod
    def get_or_create_client(self, user_email: str) -> 'Client':
        pass

    @abc.abstractmethod
    def get_promo_code(self, pk: PromoCodeId): ...

    @abc.abstractmethod
    def get_services(self, slugs: t.List[str]) -> t.List[Service]: ...

    @abc.abstractmethod
    def get_or_create_character(
        self,
        bungie_profile: BungieProfile,
        character_id: str,
        character_class: DestinyCharacterClass
    ) -> DestinyCharacter: ...

    @abc.abstractmethod
    def get_options(self, options_id: str) -> ServiceConfig: ...

    @abc.abstractmethod
    def create_parent_order(self, data: ParentOrder): ...

    @abc.abstractmethod
    def get_credentials(self, bungie_profile: BungieProfile) -> GameCredentials: ...

    @abc.abstractmethod
    def create_order(self, data: Order, parent_order: ParentOrder) -> Order: ...

    @abc.abstractmethod
    def get_order(self, order_id: int) -> Order:
        """
        @raise OrderNotExists: if order not found
        """

    @abc.abstractmethod
    def update_order(self, order: Order) -> t.NoReturn:
        """
        @raise OrderNotExists: if order not found
        """


class AbstractReviewRepository(abc.ABC):
    @abc.abstractmethod
    def create_review(self, review: Review): ...


class AbstractBoostersRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_discord(self, discord: DiscordId):
        pass


class OrderRepo:
    def __init__(
        self,
        db_repo: AbstractOrderRepo,
    ):
        self.db_repo = db_repo

    def get_or_create_bungie_id(
        self, bungie_profile_data: BungieProfileDTO, user: t.Union[IClient, IBooster]
    ) -> BungieProfile:
        return self.db_repo.get_or_create_bungie_id(bungie_profile_data, user)

    def get_or_create_client(self, user_email) -> Client:
        return self.db_repo.get_or_create_client(user_email)

    def get_promo_code(self, pk: PromoCodeId) -> PromoCode:
        return self.db_repo.get_promo_code(pk)

    def get_cart_products(self, slugs: t.List[str]) -> t.List[Service]:
        return self.db_repo.get_services(slugs)

    def get_or_create_character(
        self,
        bungie_profile: BungieProfile,
        character_id: str,
        character_class: DestinyCharacterClass
    ) -> DestinyCharacter:
        return self.db_repo.get_or_create_character(bungie_profile, character_id, character_class)

    def get_service_options(
        self,
        service_ids: t.List[str]
    ):
        return self.db_repo.get_services(service_ids)

    def get_credentials(self, bungie_profile: BungieProfile) -> GameCredentials:
        return self.db_repo.get_credentials(bungie_profile)

    def create_parent_order(self, data: ParentOrder) -> ParentOrder:
        return self.db_repo.create_parent_order(data)

    def create_order(self, data: Order, parent_order: ParentOrder) -> Order:
        return self.db_repo.create_order(data, parent_order)

    def get_order(self, order_id: OrderId) -> Order:
        return self.db_repo.get_order(order_id)

    def update_order(self, order: Order) -> t.NoReturn:
        return self.db_repo.update_order(order)


class BoostersRepo:
    def __init__(
        self,
        db_repo: AbstractBoostersRepository
    ):
        self.db_repo = db_repo

    def get_by_discord(self, discord_id: DiscordId):
        return self.db_repo.get_by_discord(discord_id)


class ReviewRepo:
    def __init__(
        self,
        db_repo: AbstractReviewRepository
    ):

        self.db_repo = db_repo

    def create_review(self, review: Review) -> Review:
        return self.db_repo.create_review(review)
