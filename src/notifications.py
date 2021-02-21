import datetime as dt
import logging
import os
import typing as t
import requests
from celery import shared_task

from boosting.settings import BOT_TOKEN, ENVIRONMENT
from core.domain.object_values import OrderId
from profiles.constants import Membership

logger = logging.getLogger(__name__)

ANDREY = "368801298"
STAS = "286739018"

telegram_ids_to_send = [STAS, ANDREY]

CREDENTIIALS_TEMPLATE = """

credentials:

🤫 email: {email}
🤫 password: {password}
"""

MESSAGE_TEMPLATE = """
Service: {service}
price: {price}

Platform: #{platform}
Character class: #{char_class}
Promocode: {promo}

user: {user_email}
username: {username}

"""

OPTIONS_TEMPLATE = """
    ⚡️ {description} — ${price}
    
"""

telegram_api = f"https://api.telegram.org/{BOT_TOKEN}/sendMessage"


def send_message(json):
    print("Sending message")
    response = requests.post(telegram_api, json=json)
    print(response.json())
    return response


@shared_task
def send_telegram_message_order_created(
    service: str, price: str, platform: Membership, char_class: str, promo: str, option: t.Optional[t.Any], options: str,
    user_email: str, username: str
):
    for user_id in telegram_ids_to_send:
        text = MESSAGE_TEMPLATE.format(
            service=service,
            price=price,
            platform=platform,
            user_email=user_email,
            char_class=char_class,
            promo=promo,
            username=username
        )

        for option in options:
            text += OPTIONS_TEMPLATE.format(
                description=option["description"], price=option["price"]
            )

        send_message(dict(chat_id=user_id, text=text))


def get_order_link(order_id: OrderId) -> str:
    return f'https://littlelight.store/api/destiny2/admin/orders/parentorder/{order_id}/change/'


@shared_task
def send_order_not_created(order_id: OrderId):
    order_link = get_order_link(order_id)

    text = f"""🚨 \[{ENVIRONMENT.upper()}\] [<Order id='{order_id}' datetime='{dt.datetime.now()}'>]({order_link}) 
not created
    """
    for user_id in telegram_ids_to_send:
        send_message(dict(chat_id=user_id, text=text, parse_mode='Markdown'))


@shared_task
def send_booster_assigned(order_id: OrderId, booster_username: str):
    order_link = get_order_link(order_id)

    text = f"""\[{ENVIRONMENT.upper()}\] [<Order id='{order_id}'>]({order_link}) 
booster {booster_username} is assigned
    """
    for user_id in [ANDREY]:
        send_message(dict(chat_id=user_id, text=text, parse_mode='Markdown'))


@shared_task
def new_chat_message(text: str):
    for user_id in telegram_ids_to_send:
        send_message(dict(chat_id=user_id, text=text, parse_mode='Markdown'))


class TelegramClient:
    def __init__(
        self,
        telegram_token: str
    ):
        self.telegram_token = telegram_token

    def make_call(self, user_ids: t.List[str], text: str):
        _url = f"https://api.telegram.org/{self.telegram_token}/sendMessage"
        connect_timeout, read_timeout = 5.0, 30.0
        print(f'Sending message to {_url} message: {text}')

        for user_id in user_ids:
            response = requests.post(_url, json=dict(
                chat_id=user_id,
                text=text,
                parse_mode='Markdown'
            ), timeout=(connect_timeout, read_timeout))

            print(response)
