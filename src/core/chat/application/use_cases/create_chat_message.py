import datetime as dt
from pydantic import BaseModel

from core.chat.application.repository import ChatMessagesRepository, ChatRoomRepository
from core.chat.domain.chat_room import ChatRole


class CreateChatMessageDTOInput(BaseModel):
    role: ChatRole
    text: str
    user_id: int
    order_objective_id: str


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
    ):
        self.chat_messages_repository = chat_messages_repository
        self.chat_rooms_repository = chat_rooms_repository

    def execute(self, dto: CreateChatMessageDTOInput):

        chat_room = self.chat_rooms_repository.get_chat_room(
            user_id=dto.user_id,
            order_objective_id=dto.order_objective_id,
            role=dto.role
        )

        message = chat_room.create_message(
            dto.role,
            dto.text,
        )

        self.chat_messages_repository.create(message)

        return CreateChatMessageDTOOutput(
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            created_at=message.created_at,
            text=message.text,
            role=dto.role
        )
