import logging
import typing as t
import requests
from celery import shared_task

from boosting.settings import BOT_TOKEN
from core.domain.object_values import OrderId

logger = logging.getLogger(__name__)

ANDREY = "368801298"
STAS = "286739018"

telegram_ids_to_send = [STAS, ANDREY]

telegram_api = f"https://api.telegram.org/{BOT_TOKEN}/sendMessage"


def send_message(json):
    print("Sending message")
    response = requests.post(telegram_api, json=json)
    print(response.json())
    return response


def new_send_message(
    url: str,
    user_id: str,
    text: str
):
    connect_timeout, read_timeout = 5.0, 30.0

    response = requests.post(url, json=dict(
        chat_id=user_id,
        text=text,
        parse_mode='Markdown'
    ), timeout=(connect_timeout, read_timeout))

    print(response)


def get_order_link(order_id: OrderId) -> str:
    return f'https://littlelight.store/api/destiny2/admin/orders/parentorder/{order_id}/change/'


@shared_task
def new_chat_message(text: str):
    for user_id in telegram_ids_to_send:
        send_message(dict(chat_id=user_id, text=text, parse_mode='Markdown'))


@shared_task
def broadcast_message(
    url: str, users: t.List[str], message: str
):
    for user_id in users:
        new_send_message(
            user_id=user_id,
            text=message,
            url=url
        )


class TelegramClient:
    def __init__(
        self,
        telegram_token: str
    ):
        self.telegram_token = telegram_token

    def make_call(self, user_ids: t.List[str], text: str):
        _url = f"https://api.telegram.org/{self.telegram_token}/sendMessage"
        print(f'Sending message to {_url} message: {text}')

        broadcast_message.delay(
            users=user_ids,
            message=text,
            url=_url
        )
