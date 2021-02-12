import typing as t

from profiles.constants import Membership


class Client:
    def __init__(
        self,
        _id: int,
        email: str,
        username: str,
        avatar: t.Optional[str] = None,
        discord: t.Optional[str] = None,
    ):
        self.avatar = avatar
        self.username = username
        self.id = _id
        self.email = email
        self.discord = discord

    def __repr__(self):
        return f"Client: id={self.id} username={self.username}"


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
