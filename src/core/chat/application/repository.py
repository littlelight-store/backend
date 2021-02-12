import typing as t
import abc

from core.chat.domain.chat_room import ChatRole, ChatRoom, ChatMessage


class ChatRoomRepository(abc.ABC):
    @abc.abstractmethod
    def get_chat_room(
        self,
        user_id: int,
        order_objective_id: str,
        role: ChatRole
    ) -> ChatRoom:
        pass

    @abc.abstractmethod
    def list_rooms_by_user(self, user_id) -> t.List[ChatRoom]:
        pass


class ChatMessagesRepository(abc.ABC):
    @abc.abstractmethod
    def list_messages_by_users_pair(
        self,
        client_id: int,
        booster_id: int
    ) -> t.List[ChatMessage]:
        pass

    @abc.abstractmethod
    def create(self, message: ChatMessage):
        pass
