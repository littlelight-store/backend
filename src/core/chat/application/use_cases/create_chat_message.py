import datetime as dt
import logging

from pydantic import BaseModel

from core.application.dtos.notifications.event_notifications import EventChatMessageDTO
from core.application.repositories import EventNotificationRepository
from core.chat.application.repository import ChatMessagesRepository, ChatRoomRepository
from core.chat.domain.chat_room import ChatRole
from core.clients.application.repository import ClientsRepository
from core.clients.domain.client import Client
from core.order.application.repository import MQEventsRepository
from core.utils.map_by_key import map_by_key
from notificators.new_email import DjangoEmailNotificator

logger = logging.getLogger(__name__)


class CreateChatMessageDTOInput(BaseModel):
    role: ChatRole
    text: str
    user_id: int
    receiver_id: int


class CreateChatMessageDTOOutput(BaseModel):
    sender_id: int
    receiver_id: int
    created_at: dt.datetime
    text: str
    role: ChatRole


class CreateChatMessageUseCase:
    def __init__(
        self,
        chat_rooms_repository: ChatRoomRepository,
        chat_messages_repository: ChatMessagesRepository,
        event_repository: EventNotificationRepository,
        users_repository: ClientsRepository,
        email_notificator: DjangoEmailNotificator,
        events_repository: MQEventsRepository
    ):
        self.events_repository = events_repository
        self.email_notificator = email_notificator
        self.event_repository = event_repository
        self.chat_messages_repository = chat_messages_repository
        self.chat_rooms_repository = chat_rooms_repository
        self.users_repository = users_repository

    def execute(self, dto: CreateChatMessageDTOInput):

        chat_room = self.chat_rooms_repository.get_chat_room(
            user_id=dto.user_id,
            user_id_2=dto.receiver_id,
            role=dto.role
        )

        message = chat_room.create_message(
            dto.role,
            dto.text,
        )

        chat_sides = map_by_key(
            self.users_repository.list_by_ids([message.sender_id, message.receiver_id]),
            'id'
        )

        sender, receiver = chat_sides[message.sender_id], chat_sides[message.receiver_id]  # type: Client

        event_data = EventChatMessageDTO(
            text=message.text,
            from_=sender.username or sender.id,
            to_=receiver.username or sender.id
        )

        if receiver.can_send_email_chat_notification():
            logger.info("Message may be sent to client, sending")
            self.events_repository.new_message_send(
                from_message=sender.username,
                user_email=receiver.email
            )
            receiver.set_message_sent()

        self.users_repository.save(receiver)
        self.chat_messages_repository.create(message)
        self.event_repository.chat_message(event_data)

        return CreateChatMessageDTOOutput(
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            created_at=message.created_at,
            text=message.text,
            role=dto.role
        )
