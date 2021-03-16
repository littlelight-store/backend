# import the logging library
import logging
import urllib
from datetime import datetime, timedelta

import requests
from dependency_injector.wiring import Provide, inject
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
from profiles.models import (
    ProfileCredentials,
)
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

