# import the logging library
import logging
import urllib
from datetime import datetime, timedelta
from decimal import Decimal

import requests
from dependency_injector.wiring import Provide, inject
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from boosting.settings import ENVIRONMENT
from core.order.application.exceptions import OrderDoesNotExists
from core.order.application.use_cases.process_payment_callback_uc import (
    ProcessPaymentCallbackDTORequest,
    ProcessPaymentCallbackUseCase,
)
from infrastructure.injectors.application import ApplicationContainer
from orders.enum import OrderStatus
from orders.tasks import (
    order_created,
    send_order_created_telegram_notification,
)
from profiles.models import (
    BungieID,
    BungiePlatform,
    ProfileCredentials,
    User,
    UserCharacter,
)
from profiles.constants import Membership
from reviews.models import Review
from services.models import PromoCode, Service, ServiceConfig
from .models import Order, ParentOrder
from .serializers import (
    BoosterOrdersSerializer,
    OrderSerializer,
    ProfileCredentialsSerializer,
    UserBoosterOrderUpdateSerializer,
    UserOrderSerializer,
    UserOrderUpdateSerializer,
)

# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_cart_item_price(layout_options: dict) -> float:
    if layout_options.get("price"):
        price_obj: dict = layout_options["price"]

        if type(price_obj) == dict:
            return float(price_obj["totalPrice"])
        return float(layout_options.get("price"))


def booster_price(price, booster_percent):
    discount = price * (int(booster_percent) / 100)
    return float(price - discount)


def get_discount_price(price, promo, service_slug):
    if promo and promo.service and promo.service.filter(slug=service_slug).exists():
        return promo.calculate_discount_for_price(price)
    return price


@api_view(["POST"])
@csrf_exempt
def process_create_order(request):
    cart_data = request.data.get("cartData")
    user_data = request.data.get("accountInformation")
    payment_data = request.data.get("paymentData")
    promo_data = request.data.get("promoCode", {})
    bungie_profile_data = request.data.get("bungieProfile")
    bungie_characters_data = request.data.get("bungieCharacters")

    user_email = user_data.get("contactEmail").lower()

    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        random_password = User.objects.make_random_password()
        user = User.objects.create_user(
            email=user_email, username=user_email, password=random_password
        )
        # welcome_email_letter.delay(user_email=email)

    order_bungie_profile = None
    created_orders = []
    total_order_price = 0
    payment_id = payment_data.get("paymentId")
    invoice_number = payment_data.get("invoiceNumber")
    user_platform = None

    parent_order = ParentOrder.objects.create(
        site=get_current_site(request),
        payment_id=invoice_number,
        raw_data=request.data,
    )

    bungie_profile, created = BungieID.objects.get_or_create(
        owner=user,
        membership_id=bungie_profile_data["activeProfile"]["membershipId"],
        membership_type=bungie_profile_data["activeProfile"]["membershipType"],
        defaults=dict(
            username=bungie_profile_data["activeProfile"].get("displayName"),
        ),
    )

    promo = promo_data.get("discountObject", None)

    if promo:
        try:
            promo = PromoCode.objects.get(pk=promo["code"])
        except PromoCode.DoesNotExist:
            promo = None

    for cart_item in cart_data:
        selected_service = cart_item.get("product")

        selected_service = get_object_or_404(Service, slug=selected_service["slug"])

        selected_character = cart_item.get("characterId")
        character_data = bungie_characters_data.get(selected_character, None)

        if not character_data:
            logger.exception("Character does not exists for current profile")

        order_bungie_profile = bungie_profile

        characters = UserCharacter.objects.filter(
            bungie_profile=bungie_profile,
            character_id=character_data["characterId"],
            character_class=character_data["classType"],
        )

        character = characters.first()

        if not character:
            character = UserCharacter.objects.create(
                bungie_profile=bungie_profile,
                character_id=character_data["characterId"],
                character_class=character_data["classType"],
            )

        user_platform = int(user_data.get("platform"))

        cart_layout_options = cart_item["layoutOptions"]

        total_price = get_cart_item_price(cart_layout_options)

        discounted = get_discount_price(total_price, promo, selected_service.slug)

        order = Order.objects.create(
            parent_order=parent_order,
            bungie_profile=bungie_profile,
            character=character,
            payment_id=payment_id,
            invoice_number=invoice_number,
            promo=(
                promo
                if promo
                and promo.service
                and promo.service.filter(slug=selected_service.slug).exists()
                else None
            ),
            service=selected_service,
            booster_price=booster_price(discounted, selected_service.booster_price),
            total_price=discounted,
            site=get_current_site(request),
            raw_data=cart_item,
            layout_options=cart_layout_options,
            comment=user_data.get("comment"),
        )

        selected_modes = []

        for option_id, option in cart_layout_options.get("selectedOptions", {}).items():
            if option:
                try:
                    selected_mode = ServiceConfig.objects.get(
                        id=option_id, service=selected_service
                    )
                    selected_modes.append(selected_mode)
                except ServiceConfig.DoesNotExist:
                    continue

        for option in cart_layout_options.get("customSelectedOptions", {}):
            if option:
                try:
                    selected_mode = ServiceConfig.objects.get(
                        id=option["id"], service=selected_service
                    )
                    selected_modes.append(selected_mode)
                except ServiceConfig.DoesNotExist:
                    continue

        order.service_config.set(selected_modes)

        total_order_price += float(order.total_price)

        created_orders.append(order)

    bungie_platform = BungiePlatform.objects.get(value=user_platform)

    credentials = None

    try:
        credentials = ProfileCredentials.objects.get(
            platform=bungie_platform,
            owner=user
        )
    except ProfileCredentials.DoesNotExist:
        pass

    parent_order.total_price = Decimal(int(total_order_price))
    parent_order.invoice_number = invoice_number
    parent_order.platform = bungie_platform
    parent_order.credentials = credentials

    parent_order.save()

    review = Review.objects.create(author=user, order=parent_order)

    review.services.set([order.service for order in created_orders])

    resp = {"user": user.pk, "parent_order": parent_order.pk, "status": "ok"}

    if order_bungie_profile:
        resp["bungie_id"] = order_bungie_profile.pk

    if settings.ENVIRONMENT == "prod":

        order_created.delay(
            user_email=user.email,
            username=bungie_profile_data.get("username"),
            order_number=payment_id,
            order_info=[order.order_info() for order in created_orders],
            platform=Membership(user_platform).name,
            total=total_order_price,
        )

        send_order_created_telegram_notification.delay(
            platform=Membership(user_platform).name,
            order_info=[order.order_info() for order in created_orders],
            user_email=user.email,
            username=bungie_profile_data.get("username")
        )

    return Response(resp)


class OrderCompletedLastWeekAPIView(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        one_week_ago = datetime.today() - timedelta(days=7)
        queryset = Order.on_site.select_related("service").filter(
            created_at__gte=one_week_ago
        )
        slug = self.request.query_params.get("slug", None)
        if slug is not None:
            queryset = queryset.filter(service__slug=slug)
        return queryset.order_by("-created_at")


@api_view(["POST"])
@permission_classes((permissions.AllowAny,))
@inject
def invoice_complete(
    request,
    uc: ProcessPaymentCallbackUseCase = Provide[ApplicationContainer.orders_uc.process_payment_callback_uc]
):
    VERIFY_URL_PROD = "https://ipnpb.paypal.com/cgi-bin/webscr"
    VERIFY_URL_TEST = "https://ipnpb.sandbox.paypal.com/cgi-bin/webscr"

    if ENVIRONMENT == "prod":
        # Switch as appropriate
        VERIFY_URL = VERIFY_URL_PROD
    else:
        VERIFY_URL = VERIFY_URL_TEST

    # Read and parse query string
    param_str = request.body.decode("utf-8").strip()
    params = urllib.parse.parse_qsl(param_str)

    # Add '_notify-validate' parameter
    params.append(("cmd", "_notify-validate"))

    # Post back to PayPal for validation

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Python-IPN-Verification-Script",
    }

    r = requests.post(VERIFY_URL, params=params, headers=headers, verify=True)
    r.raise_for_status()

    # # Check return message and take action as needed
    if r.text == "VERIFIED":
        req_data = request.data
        invoice_number = req_data["custom"]
        total_price = req_data["payment_gross"]

        payment_status = req_data["payment_status"]
        payment_is_complete = payment_status == "Completed"

        try:
            dto = ProcessPaymentCallbackDTORequest(
                cart_id=invoice_number,
                total_price=total_price
            )
            uc.execute(dto)
            logger.info(f'Processed new order. {invoice_number}')
        except OrderDoesNotExists:
            logger.info('New ClientOrder did not found')

            try:
                parent_order = ParentOrder.objects.get(invoice_number=invoice_number,)
                parent_order.payment_status = payment_status
                parent_order.is_payed = payment_is_complete
                parent_order.save()
            except Order.DoesNotExist as e:
                logger.exception("Transaction was not found", exc_info=e)

            try:
                orders = Order.objects.filter(invoice_number=invoice_number,)
                if orders:
                    orders.update(
                        payment_status=payment_status, is_payed=payment_is_complete
                    )
                else:
                    logger.exception("Transaction was not found")
            except Order.DoesNotExist as e:
                logger.exception("Transaction was not found", exc_info=e)

    elif r.text == "INVALID":
        logger.info("STATUS IS INVALID")
    else:
        logger.info(r.text)

    return Response(r.text, status=status.HTTP_200_OK)


class UserOrdersView(ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = UserOrderSerializer

    def get_serializer_context(self):
        request = self.request if ENVIRONMENT == "development" else None
        return {"request": request}

    def get_queryset(self):
        return Order.objects.filter(bungie_profile__owner=self.request.user).order_by(
            "-created_at"
        )[:15]


class UserBoosterOrdersView(ListAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = BoosterOrdersSerializer

    def get_serializer_context(self):
        request = self.request if ENVIRONMENT == "development" else None
        return {"request": request}

    def get_queryset(self):
        return (
            Order.objects.filter(booster_user=self.request.user)
            .exclude(status=OrderStatus.is_checking_payment.value)
            .order_by("-created_at")
        )[:15]


class UserOrderView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = UserOrderUpdateSerializer

    def get_queryset(self):
        return Order.objects.filter(bungie_profile__owner=self.request.user)


class OrderCredentialsView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = ProfileCredentialsSerializer

    def get_object(self):
        return self.get_queryset().first()

    def get_queryset(self):
        order_id = self.kwargs.get("order_id")

        return ProfileCredentials.objects.filter(
            parentorder__orders__booster_user=self.request.user,
            parentorder__orders__id=order_id,
        )


class UserBoosterOrderView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    serializer_class = UserBoosterOrderUpdateSerializer

    def get_queryset(self):
        return Order.objects.filter(booster_user=self.request.user)


@api_view(["POST"])
@permission_classes((permissions.AllowAny,))
def accept_order(request):
    token = request.data.get('token', None)

