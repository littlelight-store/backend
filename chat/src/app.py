import logging
import os

import asyncpg
import socketio
from aiohttp import web

from src.history import get_chat_messages, save_chat_message_to_history, set_message_seen

import sentry_sdk

CHAT_SENTRY_SDN = os.environ.get("CHAT_SENTRY_SDN")

if CHAT_SENTRY_SDN:
    sentry_sdk.init(CHAT_SENTRY_SDN)

sio = socketio.AsyncServer(cors_allowed_origins=[
    'http://localhost:3000',
    'https://littlelight.store',
    'http://chat:5000',
    'https://stage.littlelight.store'
], async_mode='aiohttp')

app = web.Application()


logger = logging.getLogger(__name__)


class UserNotAuthenticated(ValueError):
    pass


class UserNotFound(ValueError):
    pass


async def get_bungie_user_info(user_id, connection):
    result = await connection.fetchrow(
        'select username, id from profiles_bungieid where owner_id=$1',
        user_id
    )
    if result is not None:
        return result
    else:
        raise ConnectionRefusedError('Client user not found failed')


async def get_booster_user_info(user_id, connection):
    result = await connection.fetchrow(
        '''
            SELECT b.username, b.id from profiles_user as u
                JOIN profiles_boosteruser bu on bu.id = u.booster_profile_id
                JOIN profiles_bungieid b on b.id = bu.in_game_profile_id
            WHERE u.id = $1
        ''',
        user_id
    )
    if result is not None:
        return result
    else:
        raise ConnectionRefusedError('Client user not found failed')


async def authenticate_user(user_token, connection):
    result = await connection.fetchrow(
        'select user_id from authtoken_token where key=$1',
        user_token
    )
    if result is not None:
        user_id = result['user_id']
        return user_id
    else:
        raise ConnectionRefusedError('authentication failed')


class OrderChatNamespace(socketio.AsyncNamespace):
    async def on_join_room(self, sid, room_name, token, role, order_id) -> None:
        pool = app['pool']

        session_data = await self.get_session(sid)

        is_booster: bool = (role == 'booster')

        # Ранее не авторизован
        if not session_data.get('user_id'):

            async with pool.acquire() as connection:
                async with connection.transaction():
                    user_id = await authenticate_user(token, connection)

                    print(f'User id: {user_id}')

                    if is_booster:
                        user_info = await get_booster_user_info(user_id, connection)
                    else:
                        user_info = await get_bungie_user_info(user_id, connection)

                    await self.save_session(sid, {
                        'user_id': user_id,
                        'role': role,
                        **user_info
                    })

        self.enter_room(sid, room_name)

        logger.debug(f'Fetching messages for: {order_id}')
        async with pool.acquire() as connection:
            async with connection.transaction():
                messages = await get_chat_messages(order_id, connection)

        if messages:
            await self.emit(
                'persist_messages',
                {
                    "messages": messages,
                    "room_name": room_name
                },
                room=room_name
            )

    async def on_send_message(self, sid, data, order_id, room_name) -> None:
        pool = app['pool']

        serssion_data = await self.get_session(sid)

        message = {
            'user_id': serssion_data.get('user_id'),
            'username': serssion_data.get('username'),
            'role': serssion_data.get('role'),
            'msg': data.get('message'),
            'created_at': data.get('createdAt')
        }

        if room_name in self.rooms(sid):
            async with pool.acquire() as connection:
                async with connection.transaction():
                    created_id = await save_chat_message_to_history(order_id, message, connection)

                    message['id'] = created_id

                    await self.emit(
                        'new_message',
                        {
                            "message": message,
                            "room_name": room_name,
                        },
                        room=room_name
                    )

    async def on_seen_message(self, sid, message_id, room_name) -> None:
        pool = app['pool']

        if room_name in self.rooms(sid):
            async with pool.acquire() as connection:
                async with connection.transaction():
                    await set_message_seen(int(message_id), connection)

                    await self.emit(
                        'seen_message',
                        message_id,
                        room=room_name
                    )


async def init_app() -> web.Application:
    app['pool'] = await asyncpg.create_pool(
        database='boosting',
        password=os.environ.get('POSTGRES_PASSWORD', 'sumes241oefsarasdea342'),
        user=os.environ.get('POSTGRES_USER', 'boosting'),
        host=os.environ.get('POSTGRES_HOST', 'localhost')
    )

    sio.register_namespace(OrderChatNamespace('/ws/order/chat'))
    sio.attach(app)

    return app


if __name__ == '__main__':
    web.run_app(init_app(), host='0.0.0.0')
