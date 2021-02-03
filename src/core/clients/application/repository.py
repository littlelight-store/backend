import typing as t
import abc

from pydantic import EmailStr

from core.clients.domain.client import Client, ClientCredential


class ClientsRepository(abc.ABC):

    @abc.abstractmethod
    def get_or_create_by_email(self, email: EmailStr) -> Client:
        pass

    @abc.abstractmethod
    def get_by_id(self, client_id: int) -> Client:
        pass

    @abc.abstractmethod
    def save(self, client: Client):
        pass


class ClientCredentialsRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_user_id_and_platform(self, platform: str, user_id: int):
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

