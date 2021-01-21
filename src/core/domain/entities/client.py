import typing as t

from core.domain.entities.interfaces import IClient
from core.domain.object_values import ClientId
from profiles.constants import Membership


class Client(IClient):
    def __init__(
        self,
        email: str,
        client_id: t.Optional[ClientId] = None
    ):
        self.email = email
        self.client_id = client_id


class GameCredentials:
    def __init__(
        self,
        name: str,
        password: str,
        platform: int,
        credentials_id: int
    ):
        self.password = password
        self.name = name
        self.platform = Membership(platform)
        self.id = credentials_id
