import enum
import typing as t
import datetime as dt

from django.utils import timezone


class ChatRole(str, enum.Enum):
    client = 'client'
    booster = 'booster'


class ChatRoomOrderDetails:
    def __init__(
        self,
        service_title: str,
        price: str,
        image: str
    ):
        self.image = image
        self.price = price
        self.service_title = service_title


class ChatRoom:
    def __init__(
        self,
        client_id: int,
        booster_id: int,
        messages: t.List['ChatMessage'] = None,
    ):
        if not messages:
            messages = []

        self.messages = messages
        self.booster_id = booster_id
        self.client_id = client_id

    def create_message(self, role: ChatRole, text: str) -> 'ChatMessage':
        sender_id, receiver_id = (self.booster_id, self.client_id) if \
            role == ChatRole.booster else \
            (self.client_id, self.booster_id)

        return ChatMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            created_at=dt.datetime.now(tz=timezone.utc),
            text=text,
        )

    def __repr__(self):
        return f"ChatRoom: ClientId: {self.client_id} BoosterId: {self.booster_id} messages: {len(self.messages)}"


class ChatMessage:
    def __init__(
        self,
        sender_id: int,
        receiver_id: int,
        created_at: dt.datetime,
        text: str,
    ):
        self.text = text
        self.created_at = created_at
        self.receiver_id = receiver_id
        self.sender_id = sender_id
