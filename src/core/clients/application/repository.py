import typing as t
import abc

from pydantic import EmailStr

from core.clients.domain.client import Client, ClientCredential
from profiles.constants import Membership


class ClientsRepository(abc.ABC):

    @abc.abstractmethod
    def get_or_create_by_email(self, email: EmailStr) -> Client:
        pass

    @abc.abstractmethod
    def get_by_id(self, client_id: int) -> Client:
        pass

    @abc.abstractmethod
    def list_by_ids(self, client_id: t.List[int]) -> t.List[Client]:
        pass

    @abc.abstractmethod
    def save(self, client: Client):
        pass


class ClientCredentialsRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_user_id_and_platform(self, platform: Membership, user_id: int) -> ClientCredential:
        """
        @raise ProfileCredentialsNotFound if profile credentials not found
        """

    @abc.abstractmethod
    def list_by_user(self, user_id: int) -> t.List[ClientCredential]:
        pass

    @abc.abstractmethod
    def list_by_booster_and_orders(self, booster_id: int, client_order_ids: t.List[str]) -> t.List[ClientCredential]:
        pass

    @abc.abstractmethod
    def save(self, credentials: ClientCredential):
        pass

