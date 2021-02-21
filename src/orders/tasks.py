import logging
import typing as t

from celery import shared_task
from dependency_injector.wiring import Provide, inject
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from boosting.settings import IS_PROD, TRUSTPILOT_BCC
from core.order.application.use_cases.order_created_notifications import OrderCreatedNotificationsUseCaseDTOInput
from core.order.application.use_cases.status_callbacks.order_pending_approval import \
    OrderPendingApprovalCallbackDTORequest
from infrastructure.injectors.application import ApplicationContainer

from notifications import send_telegram_message_order_created
from profiles.constants import Membership

logger = logging.getLogger(__name__)


def get_dashboard_url():
    return f"{settings.BASE_URL}/dashboard"


def _build_order_msg(
    username, order_number, platform, order_info, total
):
    text = (
        f"Hi, {username}"
        f"We have started processing your order. Our Manager will contact you shortly with further details.\n\n"
        f"Your Order Number: {order_number}\n"
        f"Your platform: {platform}\n"
        f"\n"
        f"We have started processing your order. Our Manager will contact you shortly with further details.\n"
        f"Order summary:\n"
    )

    for order in order_info:
        text += f'{order["title"]} — {order["price"]}\n'

    text += f"Total: ${total}\n"
    text += f"Thank you for your purchase from littlelight.store\n\n"
    return text


def _new_build_order_msg(
    order_number, order_info, total
):
    text = (
        f"Hi"
        f"We have started processing your order. Our Manager will contact you shortly with further details.\n\n"
        f"Your Order Number: {order_number}\n"
        f"\n"
        f"We have started processing your order. Our Manager will contact you shortly with further details.\n"
        f"Order summary:\n"
    )

    for order in order_info:
        text += f'{order}\n'

    text += f"Total: ${total}\n"
    text += f"Thank you for your purchase from littlelight.store\n\n"
    return text


def _build_2fa_message(username):
    text = (
        f"Hi, {username}"
        f"Our booster is trying to log in to your account.\n\n"
        f"However, account information you provided is incorrect. "
        f"Please check and tell the correct one to your booster in the chat in our Dashboard"
        f"However, we need a two-factor authorization code to start or continue with your order. "
        f"Please check your email/phone and tell the code to your booster in the chat in our Dashboard."
    )
    return text


def _build_incorrect_credentials_message(username):
    text = (
        f"Hi, {username}"
        f"Our booster is trying to log in to your account.\n\n"
        f"However, account information you provided is incorrect. "
        f"Please check and tell the correct one to your booster in the chat in our Dashboard"
    )
    return text


def _build_pending_approval(services):
    text = (
        f"The following services has been completed:\n\n"
        f"{services}"
        f"We await confirmation of completion on your part."
        f"To do this, please log in to the dashboard and mark the order "
        f"completed after you check your account.\n\n"
        f"Attention!\n"
        f"Your order will automatically be considered completed if you do not confirm or deny it within 48 hours."
    )

    return text


@shared_task
def order_created(
    user_email, order_number, platform,
    order_info, total: str, username,
):
    subject, from_email, to = (
        "Order information",
        settings.DEFAULT_FROM_EMAIL,
        user_email,
    )
    text_content = _build_order_msg(
        username, order_number, platform, order_info, total
    )

    print(order_info)

    html_content = render_to_string(
        "orders/new_email.html",
        {
            "order_number": order_number,
            "platform": platform,
            "username": username,
            "services": order_info,
            "total": total,
            "hide_unsubscribe": True,
        },
    )

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def new_order_created(
    total_price: str,
    order_id: str,
    services: t.List[str],
    user_email: str,
    platform: str
):
    subject, from_email, to = (
        "Order information",
        settings.DEFAULT_FROM_EMAIL,
        user_email,
    )
    text_content = _new_build_order_msg(
        order_id, services, total_price
    )

    html_content = render_to_string(
        "orders/order_info.html",
        {
            "order_number": order_id[:6],
            "services": services,
            "total": total_price,
            "platform": platform
        },
    )

    bcc = []

    if IS_PROD:
        bcc = [TRUSTPILOT_BCC]

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to], bcc=bcc)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def required_2_fa_code(user_email, username):
    subject, from_email, to = (
        "2FA code required",
        settings.DEFAULT_FROM_EMAIL,
        user_email,
    )

    dashboard_url = get_dashboard_url()

    text_content = _build_2fa_message(username)
    html_content = render_to_string(
        "orders/status/2_fa_required.html",
        {"username": username, "dashboard_link": dashboard_url},
    )

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def incorrect_credentials(user_email, username):
    subject, from_email, to = (
        "Wrong account information!",
        settings.DEFAULT_FROM_EMAIL,
        user_email,
    )

    dashboard_url = get_dashboard_url()

    text_content = _build_incorrect_credentials_message(username)
    html_content = render_to_string(
        "orders/status/invalid-credentials.html",
        {"username": username, "dashboard_link": dashboard_url},
    )

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def pending_approval(user_email, services):
    subject, from_email, to = (
        "Your order has been completed",
        settings.DEFAULT_FROM_EMAIL,
        user_email,
    )

    text_content = _build_pending_approval(services)
    html_content = render_to_string(
        "orders/status/new/pending-approval.html",
        {"services": services, "email": user_email},
    )

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def chat_message_unread(user_email: str, from_message: str):
    subject, from_email, to = (
        "New Order Chat Message",
        settings.DEFAULT_FROM_EMAIL,
        user_email,
    )

    text_content = f"New chat message from: {from_message}"
    html_content = render_to_string(
        "orders/chat/new/new_chat_message.html",
        {"sender_username": from_message, "email": user_email},
    )

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def send_order_created_telegram_notification(
    platform: Membership,
    order_info: t.List[t.Dict[str, str]],
    user_email: str,
    username: str
):
    for order in order_info:
        send_telegram_message_order_created(
            service=order["title"],
            price=order["price"],
            platform=platform,
            char_class=order["character_class"],
            promo=order["promo"],
            option=order["option"],
            options=order["options"],
            user_email=user_email,
            username=username
        )


@shared_task
@inject
def order_created_notifications(
    client_order_id: str,
    uc=Provide[ApplicationContainer.orders_uc.order_created_notifications_uc]
):
    # "9b843b81d3c6437cb05b5213d02448eb"
    uc.execute(
        OrderCreatedNotificationsUseCaseDTOInput(
            client_order_id=client_order_id
        )
    )


@shared_task
@inject
def set_pending_approval_task(
    order_objective_id,
    uc=Provide[ApplicationContainer.orders_status_uc.order_pending_approval_uc]
):
    logger.info(f'Starting task set_pending_approval_task with {order_objective_id}')

    dto = OrderPendingApprovalCallbackDTORequest(
        order_objective_id=order_objective_id
    )
    uc.execute(dto)
