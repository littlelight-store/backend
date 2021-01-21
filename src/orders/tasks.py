import datetime as dt
import logging
import random
import typing as t

from celery import shared_task
from dependency_injector.wiring import Provide, inject
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from core.order.application.use_cases.order_created_notifications import OrderCreatedNotificationsUseCaseDTOInput
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


def _build_pending_approval(username, order_info):
    text = (
        f"Hi, {username}"
        f"The following service has been completed:\n\n"
        f"{order_info['title']} — {order_info['price']}"
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

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
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
def pending_approval(user_email, username, order_info):
    subject, from_email, to = (
        "Your order has been completed",
        settings.DEFAULT_FROM_EMAIL,
        user_email,
    )

    dashboard_url = get_dashboard_url()

    text_content = _build_pending_approval(username, order_info)
    html_content = render_to_string(
        "orders/status/pending-approval.html",
        {"username": username, "service": order_info, "dashboard_link": dashboard_url},
    )

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


@shared_task
def order_created_admin():
    subject, from_email = (
        "!!! NEW ORDER ON LITTELIGHT.store !!!",
        settings.DEFAULT_FROM_EMAIL,
    )

    msg = EmailMultiAlternatives(
        subject,
        "HEY! CHECK THIS OUT. NEW ORDER",
        from_email,
        ["mamosiko@gmail.com", "littlelight.boost@gmail.com"],
    )
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


def _build_new_message(username, role):
    if role == "booster":
        return (
            f"Hi, {username}"
            f"You have received a new message from your client.\n"
            f"Please visit the Dashboard and check this out."
        )
    elif role == "client":
        return (
            f"Hi, {username}"
            f"You have received a new message from your booster.\n"
            f"The booster is looking forward to your reply.\n"
            f"However, in case of a critical situation, you will be additionally notified of the change in order status."
        )
    else:
        return None


def send_new_year_message(emails):
    for email in emails:
        subject, from_email, to = (
            "Destiny 2 boosting Christmas and New Year sale 🎁",
            settings.DEFAULT_FROM_EMAIL,
            email,
        )

        text_content = """
            Dear friend,
            We are launching a Christmas and New Year sale. 
            We offer a 15% discount on the entire catalog. 
            But that is not all! 
            Every customer who spends at least $100 during the sale will 
            receive a personal code for a 20% discount on absolutely any 
            purchase during the next year. 
            """

        html_content = render_to_string(f"orders/new_year.html",)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


@shared_task
def send_message_to_notify_unread_messages():
    notify_threshold = 15

    from orders.models import Order

    orders = Order.get_order_with_last_unread_messages_later_than(notify_threshold)

    logger.info(f"Found orders with unread messages at chat: {len(orders)}")

    for order in orders:
        logger.info(f"Sending message with unread message to {order.send_to}")

        if order.send_to == "booster":
            booster_user = order.booster_user

            if booster_user and booster_user.booster_profile.in_game_profile:
                email = booster_user.email
                username = booster_user.booster_profile.in_game_profile.username
                # send_new_message_pending_message(username, email, "booster")
            else:
                logger.exception(
                    "Found order without booster user with pending message"
                )
        elif order.send_to == "client":
            user = order.bungie_profile.owner
            email = user.email
            username = user.username
            # send_new_message_pending_message(username, email, "client")
        order.save()


customer_amount_items_chosen = [
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    2,
    2,
    2,
    2,
    3,
]

services_to_chose = [
    *["garden-of-salvation"] * 7,
    *["trials-of-osiris"] * 10,
    *["weekly-pinnacle-rewards"] * 8,
    *["pit-of-heresy"] * 5,
]


@shared_task
def accept_pending_orders():
    from orders.models import Order
    from orders.enum import OrderStatus

    date = dt.datetime.now() - dt.timedelta(days=2)

    orders = Order.objects.filter(
        status=OrderStatus.pending_approval.value,
        complete_at__lte=date
    )

    for order in orders:
        order.status = OrderStatus.is_complete.value
        order.save()


@shared_task
def _fake_customer():
    from orders.models import Order
    from orders.enum import OrderStatus
    from services.models import Service

    def clear_old_models():
        Order.objects.filter(is_faked=True, created_at_gte=True)

    user_is_quited = random.choice([0, 1])

    print(f"User is quited: {user_is_quited}")

    if not user_is_quited:
        number_of_items_he_got = random.choice(customer_amount_items_chosen)

        print(f"He got {number_of_items_he_got} items")

        taken_services = []
        for _ in range(0, number_of_items_he_got):
            services_to_decide = [
                service
                for service in services_to_chose
                if service not in taken_services
            ]
            service_he_got = random.choice(services_to_decide)
            print(f"Got service: {service_he_got}")

            try:
                service = Service.objects.get(slug=service_he_got)
            except Service.DoesNotExist:
                pass
            else:
                order = Order.objects.create(
                    service=service,
                    is_faked=True,
                    taken_at=dt.datetime.now(),
                    status=OrderStatus.in_progress.value,
                    site_id=1,
                )
                print(f"Created order: {order}")
                taken_services.append(service_he_got)


@shared_task
def _change_old_orders_status():
    from orders.models import Order
    from orders.enum import OrderStatus

    min_complete_time = dt.datetime.now() - dt.timedelta(hours=5)

    # taken_at = 21.02.2019 - 00:00
    # now - 21.02.2019 - 18:00
    # min = 21.02.2019 - 11:00
    # max = 20.02.2019 - 18:00

    orders = (
        Order.objects.filter(taken_at__lte=min_complete_time, is_faked=True)
        .exclude(status=OrderStatus.is_complete.value)
        .order_by("taken_at")
    )

    print(f"Got orders: {len(orders)}")

    num_orders_will_be_updated = [*[1] * 6, *[2] * 3, *[3] * 1]

    order_to_update = random.choice(num_orders_will_be_updated)
    print(f"Will be updated: {order_to_update}")

    for order in orders:
        print(f"Count orders to update: {order_to_update}")
        if order_to_update:
            order_to_update -= 1
            is_complete = random.choice([0, 1])

            print(f"Will complete: {is_complete}")

            if is_complete:
                order.status = OrderStatus.is_complete.value
                order.save()


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
