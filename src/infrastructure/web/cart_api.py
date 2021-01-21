import logging

from dependency_injector.wiring import Provide, inject
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from core.domain.entities.shopping_cart.exceptions import ShoppingCartDoesNotExists
from core.exceptions import BaseNotExistsException
from core.shopping_cart.application.use_cases.add_to_shopping_cart import (
    AddItemToShoppingCartDTOInput,
    AddItemToShoppingCartUseCase,
)
from core.shopping_cart.application.use_cases.apply_promo import ApplyPromoUseCase, ApplyPromoUseCaseDTOInput
from core.shopping_cart.application.use_cases.cart_payed import CartPayedDTORequest, CartPayedUseCase
from core.shopping_cart.application.use_cases.list_shopping_cart import (
    ListShoppingCartDTOInput,
    ListShoppingCartUseCase,
)
from core.shopping_cart.application.use_cases.remove_cart_item import RemoveCartItemDTOInput, RemoveCartItemUseCase
from infrastructure.injectors.application import ApplicationContainer
from orders.services import ShoppingCartService

logger = logging.getLogger(__name__)
CART_COOKIE_NAME = '_destiny-cart-id'
SET_CREDENTIALS_COOKIE_NAME = '_set-credentials-cookie-name'


@api_view(["POST"])
@csrf_exempt
@authentication_classes([])
def add_item_to_cart(request):

    cart_id = request.COOKIES.get(CART_COOKIE_NAME)

    data = request.data

    dto = AddItemToShoppingCartDTOInput(
        cart_id=cart_id,
        adding_to_cart=data.get('adding_to_cart')
    )

    uc: AddItemToShoppingCartUseCase = ShoppingCartService.add_item_uc()

    try:
        result = uc.execute(dto)
        response = JsonResponse(result.dict(by_alias=True), status=201)

        response.set_cookie(
            CART_COOKIE_NAME, result.cart_id,
            path='/api/destiny2/',
            httponly=True,
        )

        return response
    except ShoppingCartDoesNotExists:
        response = JsonResponse(status=404, data=[], safe=False)
        response.delete_cookie(CART_COOKIE_NAME)
        return response
    except Exception as e:
        logger.exception(e)
        return JsonResponse(e, status=400)


@api_view(["GET"])
@csrf_exempt
@authentication_classes([])
def list_cart_items(request):
    cart_id = request.COOKIES.get(CART_COOKIE_NAME)

    dto = ListShoppingCartDTOInput(
        cart_id=cart_id,
    )

    uc: ListShoppingCartUseCase = ShoppingCartService.list_items_uc()

    try:
        result = uc.execute(dto)
        response = JsonResponse(result.dict(by_alias=True), status=200)
        return response
    except ShoppingCartDoesNotExists:
        response = JsonResponse(status=404, data=[], safe=False)
        response.delete_cookie(CART_COOKIE_NAME)
        return response
    except Exception as e:
        logger.exception(e)
        return JsonResponse(e, status=400)


@api_view(["POST"])
@csrf_exempt
@authentication_classes([])
@inject
@transaction.atomic
def cart_payed(
    request,
    uc=Provide[ApplicationContainer.cart_uc.cart_payed_uc]
):
    cart_id = request.COOKIES.get(CART_COOKIE_NAME)

    payment_id = request.data.get('payment_id')
    user_email = request.data.get('user_email')
    user_discord = request.data.get('user_discord')
    comment = request.data.get('comment')

    dto = CartPayedDTORequest(
        cart_id=cart_id,
        payment_id=payment_id,
        user_email=user_email,
        user_discord=user_discord,
        comment=comment
    )

    try:
        result = uc.execute(dto)
        response = JsonResponse(result.dict(), status=201)
        response.delete_cookie(CART_COOKIE_NAME)
        if result.should_set_credentials:
            response.set_cookie(
                SET_CREDENTIALS_COOKIE_NAME, True,
                path='/',
                httponly=False,
            )
        return response
    except Exception as e:
        logger.exception(e)
        return Response(str(e), status=400)


@api_view(["DELETE"])
@csrf_exempt
@authentication_classes([])
def cart_delete(request):
    cart_id = request.COOKIES.get(CART_COOKIE_NAME)
    cart_item_id = request.data.get('cart_item_id')

    dto = RemoveCartItemDTOInput(
        cart_id=cart_id,
        cart_item_id=cart_item_id
    )

    uc: RemoveCartItemUseCase = ShoppingCartService.remove_cart_item_uc()

    try:
        result = uc.execute(dto)
        response = JsonResponse(result.dict(), status=201)
        return response
    except Exception as e:
        logger.exception(e)
        return Response(str(e), status=400)


@api_view(["POST"])
@csrf_exempt
@authentication_classes([])
def apply_promo(request):
    cart_id = request.COOKIES.get(CART_COOKIE_NAME)

    dto = ApplyPromoUseCaseDTOInput(
        code=request.data.get('code'),
        cart_id=cart_id
    )

    uc: ApplyPromoUseCase = ShoppingCartService.apply_promo_uc()

    try:
        result = uc.execute(dto)
        response = JsonResponse(result.dict(), status=200)
        return response
    except BaseNotExistsException:
        return Response(status=404)
    except Exception as e:
        logger.exception(e)
        return Response(str(e), status=400)
