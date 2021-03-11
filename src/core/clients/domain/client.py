import typing as t
import datetime as dt
from decimal import Decimal

from django.utils import timezone

from profiles.constants import Membership


class Client:
    def __init__(
        self,
        _id: int,
        email: str,
        username: t.Optional[str],
        cashback: Decimal = Decimal(0),
        avatar: t.Optional[str] = None,
        discord: t.Optional[str] = None,
        last_chat_message_send_at: t.Optional[dt.datetime] = None,
    ):
        self.last_chat_message_send_at = last_chat_message_send_at
        self.cashback = cashback
        self.avatar = avatar
        self.username = username
        self.id = _id
        self.email = email
        self.discord = discord

    def has_enough_cashback(self, cashback: Decimal):
        return (self.cashback - cashback) >= 0

    def subtract_cashback(self, cashback: Decimal):
        if self.has_enough_cashback(cashback):
            self.cashback - cashback

    def add_cashback(self, total_price: Decimal, percent: int):
        cashback = total_price / 100 * percent
        self.cashback += cashback

    def can_send_email_chat_notification(self):
        now = timezone.now()
        if not self.last_chat_message_send_at:
            return True
        diff = (now - self.last_chat_message_send_at)
        return diff >= dt.timedelta(hours=1)

    def set_message_sent(self):
        self.last_chat_message_send_at = timezone.now()

    def __repr__(self):
        return f"Client: id={self.id} username={self.username}"


class ClientCredential:
    def __init__(
        self,
        account_name: str,
        account_password: str,
        platform: Membership,
        owner_id: int,
        is_expired: bool,
        has_second_factor: bool
    ):
        self.owner_id = owner_id
        self.platform = platform
        self.account_password = account_password
        self.account_name = account_name
        self.is_expired = is_expired
        self.has_second_factor = has_second_factor

    def set_expired(self):
        """Нужен для того, чтобы отметить данные как протухшие"""
        self.is_expired = True

    def set_password(self, password: str):
        self.account_password = password
        self.is_expired = False
