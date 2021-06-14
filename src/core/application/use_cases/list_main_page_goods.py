import typing as t

from pydantic import BaseModel

from core.application.repositories.aggregates.main_page_services_repository import MainPageServicesRepository
from core.order.application.repository import OrderObjectiveRepository


class MainPageService(BaseModel):
    name: str
    price: str
    slug: str
    item_image: str


class ServicesByGroupTags(BaseModel):
    tag_name: str
    tag_value: str
    items: t.List[MainPageService]


class ListMainPageGoodsDTOOutput(BaseModel):
    categories: t.List[ServicesByGroupTags]
    total_orders_in_progress: int


class ListMainPageGoodsUseCase:
    def __init__(
        self,
        main_page_services_repository: MainPageServicesRepository,
        objectives_repository: OrderObjectiveRepository
    ):
        self.objectives_repository = objectives_repository
        self.main_page_services_repository = main_page_services_repository

    def execute(self) -> ListMainPageGoodsDTOOutput:
        mapped_short_services = self.main_page_services_repository.list_main_page_goods()
        total_orders_in_progress = self.objectives_repository.count_orders_in_progress()

        return ListMainPageGoodsDTOOutput(
            categories=[ServicesByGroupTags(
                tag_name=group.name,
                tag_value=group.value,
                items=[MainPageService(
                    name=c.title,
                    price=c.price_tag,
                    slug=c.slug,
                    item_image=c.image
                ) for c in services]
            ) for group, services in mapped_short_services.items()],
            total_orders_in_progress=5 + total_orders_in_progress
        )
