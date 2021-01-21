import logging

from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from boosting.settings import ENVIRONMENT
from orders.models import Order
from reviews.models import Review
from .models import Category, PromoCode, Service
from .serializers import (
    CategorySerializer,
    PromoCodeSerializer,
    RelatedServicesSerializer,
    ServiceSerializer,
    ServicesSerializer,
)

# Get an instance of a logger
logger = logging.getLogger(__name__)


class CategoriesListView(ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        enabled_sevices = Prefetch(
            "services", queryset=Service.objects.filter(is_hidden=False)
        )
        return Category.on_site.prefetch_related(enabled_sevices).all()


@method_decorator(cache_page(60 * 30), name="dispatch")
class ServicesListView(ListAPIView):
    serializer_class = ServicesSerializer

    def get_serializer_context(self):
        request = self.request if ENVIRONMENT == "development" else None
        return {"request": request}

    def get_queryset(self):
        return (
            Service.objects.select_related("category")
            .order_by("ordering")
            .prefetch_related(
                "extra_categories",
                "seasons",
                Prefetch("reviews", queryset=Review.objects.filter(is_posted=True)),
            )
            .filter(category__site=get_current_site(self.request), is_hidden=False)
        )


class ServicesRelatedListView(ListAPIView):
    serializer_class = RelatedServicesSerializer

    def get_serializer_context(self):
        request = self.request if ENVIRONMENT == "development" else None
        return {"request": request}

    def get_queryset(self):
        return Service.objects.filter(
            category__site=get_current_site(self.request), is_hidden=False
        ).order_by("?")


@method_decorator(cache_page(60 * 30), name="dispatch")
class ServiceView(RetrieveAPIView):
    serializer_class = ServiceSerializer
    lookup_field = "slug"

    def get_serializer_context(self):
        request = self.request if ENVIRONMENT == "development" else None
        return {"request": request}

    def get_queryset(self):
        return Service.objects.select_related("category", "pvp_config").filter(
            category__site=get_current_site(self.request), is_hidden=False
        )


class BasePromoCodeError(BaseException):
    ERROR_TEXT = NotImplementedError


class PromoUsedForFirstPurchase(BasePromoCodeError):
    ERROR_TEXT = "Promo code may be used for the first purchase only"


class PromoNotFound(BasePromoCodeError):
    ERROR_TEXT = "Sorry, we couldn't find this promo code"


def check_promo_code(code, membership_id) -> PromoCode:
    obj = get_object_or_404(
        PromoCode.objects.filter(usage_limit__gte=1), **{"code": code,}
    )

    logger.debug(f"Matched promo {obj}")
    if obj.first_buy_only:
        found_orders = Order.objects.filter(
            bungie_profile__membership_id=membership_id
        ).count()

        if found_orders:
            logger.debug(f"Found working orders for: {membership_id}")
            raise PromoUsedForFirstPurchase

    return obj


@method_decorator(csrf_exempt, name="dispatch")
class CheckPromoView(APIView):

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        membership_id = request.data.get("membership_id", None)
        code = request.data.get("code", "")

        try:
            obj = check_promo_code(code, membership_id)
            serializer = PromoCodeSerializer(obj)
            obj.usage_limit -= 1
            obj.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BasePromoCodeError as e:
            return Response(
                {"status": e.ERROR_TEXT}, status=status.HTTP_400_BAD_REQUEST
            )
