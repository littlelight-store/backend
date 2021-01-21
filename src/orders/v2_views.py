import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from core.application.use_cases.create_order import CreateOrderDTO
from orders.models import ParentOrder
from orders.services import CreateOrderService


logger = logging.getLogger(__name__)


@api_view(["POST"])
@csrf_exempt
def create_order(request):
    account_info = request.data['accountInformation']
    payment_data = request.data['paymentData']
    order_params = CreateOrderDTO(
        user_email=account_info.get('contactEmail').lower(),
        cartData=request.data.get('cartData'),
        invoiceNumber=payment_data.get('invoiceNumber'),
        paymentId=payment_data.get('paymentId'),
        comment=account_info.get('notes'),
        platform=account_info.get('platform'),
        bungie_profile=request.data.get('bungieProfile')['activeProfile'],
        characters=request.data.get('bungieCharacters'),
        discountObject=request.data.get('promoCode', {}).get('discountObject')
    )
    use_case = CreateOrderService.use_case()
    try:
        result = use_case.set_params(order_params).execute()
        return JsonResponse(result, status=201)
    except Exception as e:
        logger.exception(e)
        order = ParentOrder.objects.create(
            payment_id=order_params.payment_id,
            site_id=1,
            raw_data=order_params.dict()
        )
        use_case.notification_repo.event_repository.order_creation_failed(order.id)
        return JsonResponse({}, status=201)
