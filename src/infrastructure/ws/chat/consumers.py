import typing as t
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel

from core.chat.application.use_cases.create_chat_message import CreateChatMessageDTOInput
from core.chat.application.use_cases.list_user_rooms import ListUserRoomsDTOInput, ListUserRoomsDTOOutput
from core.order.application.exceptions import OrderObjectiveNotExists
from infrastructure.injectors.application import ApplicationContainer

logger = logging.getLogger(__name__)


class BaseInputEvent(BaseModel):
    action: str
    payload: t.Any


class BaseOutputEvent(BaseModel):
    action: str
    payload: t.Any
    room_name: str


class ChatConsumer(AsyncJsonWebsocketConsumer):
    room_name: str
    room_group_name: str

    @staticmethod
    def self_room(user_id: int):
        return f"self_{user_id}"

    async def _init_self_room(self, user_id: int):
        room_name = self.self_room(user_id)
        await self.channel_layer.group_add(
            room_name,
            self.channel_name
        )

    @staticmethod
    def get_room_group_name(room):
        return f'chat_{room.client.id}_{room.booster.id}'

    @inject
    async def _init_rooms(
        self,
        user_id: int,
        list_rooms_uc=Provide[ApplicationContainer.chat.list_rooms_uc]
    ):
        result: ListUserRoomsDTOOutput = await database_sync_to_async(list_rooms_uc.execute)(
            ListUserRoomsDTOInput(
                role=self.role,
                user_id=user_id
            )
        )

        await self._init_self_room(user_id)
        for room in result.rooms:
            room_group_name = self.get_room_group_name(room)

            await self.channel_layer.group_add(
                room_group_name,
                self.channel_name
            )

            await self.channel_layer.group_send(
                self.self_room(user_id),
                {
                    'type': 'send_initial_rooms',
                    'room_data': room,
                    'room_name': room_group_name
                }
            )

            # Вот тут броадкастить ивент только в комнату по тому же пользователю

    async def connect(
        self,
    ):
        self._init_handlers()
        await self.accept()
        await self._init_rooms(self.scope['user'].id)

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive_json(self, data, **kwargs):
        event = BaseInputEvent(
            action=data['action'],
            payload=data['payload']
        )

        logger.info(f'Processing message: {event}')
        handler = self.get_handler(event.action)

        if handler:
            await handler(event.payload)

    ###########################
    # RECEIVE HANDLERS
    ###########################

    _handlers = {}

    def _init_handlers(self):
        self.add_handler('__new_message', self.new_chat_message)

    def add_handler(self, name, func):
        self._handlers[name] = func

    def get_handler(self, name):
        return self._handlers.get(name)

    @inject
    async def new_chat_message(
        self, data,
        uc=Provide[ApplicationContainer.chat.create_message_uc]
    ):
        message = data['message']
        role = data['role']
        order_objective_id = data['order_objective_id']
        room_name = data['room_name']
        user_id = data['user_id']

        try:
            message = await database_sync_to_async(uc.execute)((
                CreateChatMessageDTOInput(
                    text=message,
                    role=role,
                    user_id=user_id,
                    order_objective_id=order_objective_id
                )
            ))
        except OrderObjectiveNotExists:
            print("not found Order objective")
        else:
            result = BaseOutputEvent(
                action='new_message',
                payload=message,
                room_name=room_name,
            )

            await self.channel_layer.group_send(
                room_name,
                {
                    'type': 'chat_message',
                    'payload': result,
                }
            )

    ###########################
    # SEND HANDLERS
    ###########################

    async def chat_message(
        self,
        event,
    ):
        message = event['payload']
        await self.send(message.json())

    async def send_initial_rooms(
        self,
        event,
    ):
        result = BaseOutputEvent(
            action='send_initial_rooms',
            payload=event['room_data'],
            room_name=event['room_name']
        )
        await self.send(result.json())

    @property
    def role(self):
        return 'booster' if self.scope['user'].is_booster else 'client'
