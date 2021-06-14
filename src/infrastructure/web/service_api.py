from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from rest_framework.decorators import api_view

import logging

from rest_framework.request import Request

from boosting.settings import BASE_URL
from core.application.use_cases.list_main_page_goods import ListMainPageGoodsUseCase
from core.application.use_cases.service_page import ServicePageDTOInput, ServicePageUseCase
from infrastructure.injectors.application import ApplicationContainer
from infrastructure.injectors.service import DestinyServiceInjectors

logger = logging.getLogger()


class UseCaseInjectors(containers.DeclarativeContainer):

    service_page_uc = providers.Factory(
        ServicePageUseCase,
        service_rep=DestinyServiceInjectors.service_rep,
        service_configs_rep=DestinyServiceInjectors.service_configs_rep
    )


def fix_images_url(
    request: Request,
    image_url: str,
):
    return request.build_absolute_uri(BASE_URL + image_url)


@api_view(["GET"])
@inject
@cache_page(60 * 30)
def list_main_page_goods(
    request: Request,
    uc: ListMainPageGoodsUseCase = Provide[ApplicationContainer.use_cases.list_main_page_goods_uc]
):

    try:
        result = uc.execute()

        for category in result.categories:
            for item in category.items:
                item.item_image = fix_images_url(request, item.item_image)

        return JsonResponse(result.dict(), status=200)
    except Exception as e:
        logger.exception(e)
        return JsonResponse(e, status=400)


@api_view(['GET'])
@inject
@cache_page(60 * 30)
def get_service_page(
    request: Request,
    uc: ServicePageUseCase = Provide[ApplicationContainer.use_cases.get_service_detailed_info_uc],
    **kwargs
):

    data = ServicePageDTOInput(
        service_slug=kwargs.get('slug')
    )

    try:
        result = uc.execute(data)

        result.service_data.image_full = fix_images_url(request, result.service_data.image_full)
        result.service_data.image_bg = fix_images_url(request, result.service_data.image_bg)

        return JsonResponse(result.dict(), status=200)
    except Exception as e:
        logger.exception(e)
        return JsonResponse(e, status=502)

