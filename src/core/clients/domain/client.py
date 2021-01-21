import typing as t

from profiles.constants import Membership


class Client:
    def __init__(
        self,
        _id: int,
        email: str,
        discord: t.Optional[str] = None
    ):
        self.id = _id
        self.email = email
        self.discord = discord


class ClientCredential:
    def __init__(
        self,
        account_name: str,
        account_password: str,
        platform: Membership,
        owner_id: int
    ):
        self.owner_id = owner_id
        self.platform = platform
        self.account_password = account_password
        self.account_name = account_name
