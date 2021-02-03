from dependency_injector.wiring import Provide, inject
from django.http import JsonResponse

from core.boosters.application.dashboard.list_booster_dashboard_use_case import (
    ListBoosterDashboardDTOInput,
    ListBoosterDashboardUseCase,
)
from infrastructure.injectors.application import ApplicationContainer
from infrastructure.web.client_dashboard_api import BaseClientAPI
from infrastructure.web.service_api import fix_images_url


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
