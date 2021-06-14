import logging
import typing as t
from email.mime.image import MIMEImage
from functools import lru_cache

from celery import shared_task
from dependency_injector.wiring import Provide, inject
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from boosting.settings import IS_PROD, TRUSTPILOT_BCC
from core.clients.application.repository import ClientsRepository
from core.clients.application.send_web_push import SendWebPushDTORequest, SendWebPushUseCase
from core.order.application.use_cases.accept_pending_approval_orders_uc import AcceptPendingApprovalOrdersDTORequest
from core.order.application.use_cases.order_created_notifications import OrderCreatedNotificationsUseCaseDTOInput
from core.order.application.use_cases.status_callbacks.invalid_credentials import InvalidCredentialsDTORequest
from core.order.application.use_cases.status_callbacks.order_paused_callback import BoosterPausedOrderDTORequest
from core.order.application.use_cases.status_callbacks.order_pending_approval import \
    OrderPendingApprovalCallbackDTORequest
from infrastructure.injectors.application import ApplicationContainer

from notificators.new_email import DjangoEmailNotificator

logger = logging.getLogger(__name__)


def get_dashboard_url():
    return f"{settings.BASE_URL}/dashboard"


@lru_cache()
def logo_data():
    with open(finders.find('logo.svg'), 'rb') as f:
        print("Opened, starting reading")
        _logo_data = f.read()
    logo = MIMEImage(_logo_data)
    logo.add_header('Content-ID', '<logo>')
    return logo


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

    text = (
        f"The following services has been completed:\n\n"
        f"{services}"
        f"We await confirmation of completion on your part."
        f"To do this, please log in to the dashboard and mark the order "
        f"completed after you check your account.\n\n"
        f"Attention!\n"
        f"Your order will automatically be considered completed if you do not confirm or deny it within 48 hours."
    )
    text_content = text
    html_content = render_to_string(
        "orders/status/new/pending-approval.html",
        {"services": services, "email": user_email},
    )

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def paused_order(user_email, booster_username: str):
    subject, from_email, to = (
        "Your order has been paused",
        settings.DEFAULT_FROM_EMAIL,
        user_email,
    )

    text = (
        f"Order Is Paused"
    )
    text_content = text
    html_content = render_to_string(
        "orders/status/new/paused.html",
        {"booster_username": booster_username, "email": user_email},
    )

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def required_2fa_code(user_email):
    subject, from_email, to = (
        "Attention, 2FA code is required",
        settings.DEFAULT_FROM_EMAIL,
        user_email,
    )

    text = (
        "Our booster is trying to log in to your account However, we need a 2FA code to start or continue with your order."
        "Please check your email / phone and tell the code to your booster in the chat in our Dashboard:"
    )
    text_content = text
    html_content = render_to_string(
        "orders/status/new/2fa.html",
        {"email": user_email},
    )

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def invalid_credentials(user_email):
    subject, from_email, to = (
        "Attention, invalid in-game credentials",
        settings.DEFAULT_FROM_EMAIL,
        user_email,
    )

    text = (
        "Our booster is trying to log in to your account. However, account information you provided is incorrect."
        "Please check and set the correct credentials in dashboard and let yor booster know you did"
    )
    text_content = text
    html_content = render_to_string(
        "orders/status/new/2fa.html",
        {"email": user_email},
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
@inject
def new_chat_message(
    client_id: int,
    message: str,
    uc: SendWebPushUseCase = Provide[ApplicationContainer.create_chat_message_uc]
):
    dto = SendWebPushDTORequest(
        client_id=client_id,
        body=message,
        title='New order chat message',
        purpose='chat_messages',
        click_action=get_dashboard_url()
    )
    uc.execute(dto)


@shared_task
@inject
def order_created_notifications(
    client_order_id: str,
    uc=Provide[ApplicationContainer.orders_uc.order_created_notifications_uc]
):
    # "9b843b81d3c6437cb05b5213d02448eb"
    try:
        uc.execute(
            OrderCreatedNotificationsUseCaseDTOInput(
                client_order_id=client_order_id
            )
        )
    except Exception as e:
        logger.exception('Order is not fuken sent')


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


@shared_task
@inject
def set_paused_task(
    order_objective_id,
    client_id,
    uc=Provide[ApplicationContainer.orders_status_uc.set_paused_uc]
):
    logger.info(f'Starting task set_paused with {order_objective_id}')

    dto = BoosterPausedOrderDTORequest(
        order_objective_id=order_objective_id,
        client_id=client_id
    )
    uc.execute(dto)


@shared_task
@inject
def required_2fa_code_task(
    client_id,
    notificator: DjangoEmailNotificator = Provide[ApplicationContainer.email_notificator],
    clients_repository: ClientsRepository = Provide[ApplicationContainer.clients.clients_repository]
):
    client = clients_repository.get_by_id(client_id)
    notificator.required_2fa_code(client.email)


@shared_task
@inject
def invalid_credentials_task(
    order_objective_id,
    client_id,
    uc=Provide[ApplicationContainer.orders_status_uc.set_paused_uc]
):
    logger.info(f'Starting task invalid_credentials with {client_id}')

    dto = InvalidCredentialsDTORequest(
        client_id=client_id,
        order_objective_id=order_objective_id
    )
    uc.execute(dto)


@shared_task
@inject
def accept_pending_orders_task(
    uc=Provide[ApplicationContainer.orders_uc.accept_pending_orders_uc]
):
    dto = AcceptPendingApprovalOrdersDTORequest(
        now=timezone.now()
    )
    uc.execute(dto)

