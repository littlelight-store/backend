from dependency_injector import containers, providers

from core.chat.application.repository import ChatMessagesRepository, ChatRoomRepository
from core.chat.application.use_cases.create_chat_message import CreateChatMessageUseCase
from core.chat.application.use_cases.list_user_rooms import ListUserRoomsUseCase


class ChatContainer(containers.DeclarativeContainer):
    clients = providers.DependenciesContainer()
    chat_rooms_repository = providers.ExternalDependency(instance_of=ChatRoomRepository)
    chat_messages_repository = providers.ExternalDependency(instance_of=ChatMessagesRepository)

    create_message_uc = providers.Factory(
        CreateChatMessageUseCase,
        chat_rooms_repository=chat_rooms_repository,
        chat_messages_repository=chat_messages_repository
    )

    list_rooms_uc = providers.Factory(
        ListUserRoomsUseCase,
        chat_rooms_repository=chat_rooms_repository,
        users_repository=clients.clients_repository,
        chat_messages_repository=chat_messages_repository
    )
