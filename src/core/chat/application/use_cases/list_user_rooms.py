import typing as t
import datetime as dt
from pydantic import BaseModel

from core.chat.application.repository import ChatMessagesRepository, ChatRoomRepository
from core.chat.domain.chat_room import ChatMessage, ChatRole
from core.clients.application.repository import ClientsRepository
from core.utils.map_by_key import map_by_key


class ListUserRoomsDTOInput(BaseModel):
    role: ChatRole
    user_id: int


class ChatSideDTO(BaseModel):
    id: int
    username: str
    avatar: t.Optional[str] = None


class ChatMessageDTO(BaseModel):
    message: str
    created_at: dt.datetime
    sender_id: int
    receiver_id: int


class ChatRoomDTO(BaseModel):
    client: ChatSideDTO
    booster: ChatSideDTO
    messages: t.List[ChatMessageDTO]


class ListUserRoomsDTOOutput(BaseModel):
    rooms: t.List[ChatRoomDTO]


class ListUserRoomsUseCase:
    def __init__(
        self,
        chat_rooms_repository: ChatRoomRepository,
        chat_messages_repository: ChatMessagesRepository,
        users_repository: ClientsRepository
    ):
        self.chat_messages_repository = chat_messages_repository
        self.users_repository = users_repository
        self.chat_rooms_repository = chat_rooms_repository

    def execute(self, dto: ListUserRoomsDTOInput):
        rooms = self.chat_rooms_repository.list_rooms_by_user(dto.user_id)

        unique_ids = set()

        for room in rooms:
            unique_ids.add(room.client_id)
            unique_ids.add(room.booster_id)
            messages = self.chat_messages_repository.list_messages_by_users_pair(
                client_id=room.client_id,
                booster_id=room.booster_id
            )
            room.messages = messages

        chat_sides = map_by_key(
            self.users_repository.list_by_ids(list(unique_ids)),
            'id'
        )

        result = ListUserRoomsDTOOutput(rooms=[])

        for room in rooms:
            client = chat_sides[room.client_id]
            booster = chat_sides[room.booster_id]

            result.rooms.append(
                ChatRoomDTO(
                    client=ChatSideDTO(
                        avatar=None,
                        username=client.username,
                        id=client.id
                    ),
                    booster=ChatSideDTO(
                        avatar=booster.avatar,
                        username=booster.username,
                        id=booster.id
                    ),
                    messages=list(map(encode_message, room.messages))
                )
            )
        return result


def encode_message(message: ChatMessage) -> ChatMessageDTO:
    return ChatMessageDTO(
        message=message.text,
        created_at=message.created_at,
        receiver_id=message.receiver_id,
        sender_id=message.sender_id
    )


