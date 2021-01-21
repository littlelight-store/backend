import logging

import datetime as dt


logger = logging.getLogger(__name__)


async def save_chat_message_to_history(order_id, chat_message, connection):
    logger.debug('Saving message to database!!')

    message = chat_message.get('msg')
    created_at = dt.datetime.fromisoformat(chat_message.get('created_at'))
    username = chat_message.get('username')
    role = chat_message.get('role')
    user_id = chat_message.get('user_id')

    return await connection.fetchval('''
            INSERT INTO orders_chatmessage(msg, created_at, username, order_id, role, user_id, is_seen) 
            VALUES($1, $2, $3, $4, $5, $6, $7)
            RETURNING id
        ''', message, created_at, username, int(order_id), role, int(user_id), False)


async def get_chat_messages(order_id, connection):
    chat_messages = await connection.fetch('''
            SELECT msg, created_at, username, role, user_id, id, is_seen FROM orders_chatmessage WHERE order_id = $1
            ORDER BY created_at
        ''', int(order_id))

    result = []

    for message in chat_messages:
        message = dict(message)

        created_at = message['created_at']
        message['created_at'] = created_at.isoformat() if created_at else None

        result.append(message)

    return result


async def set_message_seen(message_id, connection):
    logger.debug('Setting message seen!!')

    await connection.execute('''
            UPDATE orders_chatmessage SET is_seen = true WHERE id = $1
        ''', message_id)
