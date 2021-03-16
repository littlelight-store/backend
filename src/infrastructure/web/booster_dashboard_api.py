import logging

from dependency_injector.wiring import Provide, inject
from django.http import JsonResponse

from core.boosters.application.dashboard.list_booster_dashboard_use_case import (
    ListBoosterDashboardDTOInput,
    ListBoosterDashboardUseCase,
)
from core.domain.exceptions import BoosterNotExists, UserIsNotBooster
from core.order.application.exceptions import OrderObjectiveNotExists
from core.order.application.use_cases.booster_accept_order_use_case import (
    BoosterAcceptOrderDTORequest,
    BoosterAcceptOrderUseCase,
)
from core.order.domain.exceptions import OrderIsAlreadyAccepted
from infrastructure.injectors.application import ApplicationContainer
from infrastructure.web.client_dashboard_api import BaseClientAPI
from infrastructure.web.service_api import fix_images_url

logger = logging.getLogger(__name__)


class BoosterDashboardAPI(BaseClientAPI):

    @inject
    def get(
        self,
        request,
        uc: ListBoosterDashboardUseCase = Provide[ApplicationContainer.booster_dashboard_uc.list_booster_dashboard_uc]
    ):
        dto = ListBoosterDashboardDTOInput(
            booster_id=request.user.id
        )
        res = uc.execute(dto)

        for item in res.orders:
            item.service_image = fix_images_url(request, item.service_image)

        return JsonResponse(data=res.dict(), status=200)


class BoosterDashboardAcceptOrderAPI(BaseClientAPI):
    @inject
    def get(
        self,
        request,
        uc: BoosterAcceptOrderUseCase = Provide[ApplicationContainer.booster_dashboard_uc.booster_accept_order_uc],
        **kwargs
    ):
        dto = BoosterAcceptOrderDTORequest(
            booster_user_id=request.user.id,
            order_objective_id=kwargs.get('order_id')
        )

        try:
            uc.execute(dto)
        except OrderIsAlreadyAccepted:
            return JsonResponse(data={"status": "already taken, sorry"}, status=400)
        except UserIsNotBooster:
            logger.warning("Not booster user trying to accept and order", extra={
                'user': request.user
            })
            return JsonResponse(data={"status": "not found"}, status=404)
        except (BoosterNotExists, OrderObjectiveNotExists) as e:
            logger.info(f"Not found: {str(e)}")
            return JsonResponse(data={"status": "not found"}, status=404)
        else:
            return JsonResponse(data={"status": "success"}, status=200)
