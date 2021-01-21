import typing as t
from decimal import Decimal

from pydantic import BaseModel, condecimal

from core.application.repositories.services import (
    ServiceConfigsRepository, ServiceDetailedInfoRepository,
    ServiceRepository,
)
from core.domain.entities.constants import ConfigurationType


class ServicePageDTOInput(BaseModel):
    service_slug: str


class ServiceData(BaseModel):
    title: str
    slug: str
    image_full: str
    image_bg: t.Optional[str]
    price: str
    base_price: t.Optional[int]
    configuration_type: t.Optional[ConfigurationType]
    at_least_one_option_required: bool


class StaticContent(BaseModel):
    you_will_get: t.Optional[str]
    description: t.Optional[str]
    requirements: t.Optional[str]


class ServiceStatistics(BaseModel):
    eta: str
    completed: int
    feedback_rating: str
    boosters_online: int


class ServiceConfigDTOOutput(BaseModel):
    title: str
    id: int
    description: str
    price: Decimal
    old_price: t.Optional[Decimal]
    extra_data: t.Optional[dict]


class ServicePageDTOOutput(BaseModel):
    service_data: ServiceData
    statistics: ServiceStatistics
    service_configs: t.List[ServiceConfigDTOOutput]
    range_slider_configs: t.Optional[dict]
    static_content: StaticContent


BOOSTERS_ONLINE = 10


class ServicePageUseCase:

    def __init__(
        self,
        service_detailed_info_repository: ServiceDetailedInfoRepository,
        service_configs_rep: ServiceConfigsRepository
    ):
        self.service_configs_rep = service_configs_rep
        self.service_detailed_info_repository = service_detailed_info_repository

    def execute(self, dto: ServicePageDTOInput) -> ServicePageDTOOutput:
        service = self.service_detailed_info_repository.get_by_slug(dto.service_slug)

        service_configs = self.service_configs_rep.list_by_service(service_slug=service.slug)

        return ServicePageDTOOutput(
            service_data=ServiceData(
                title=service.title,
                slug=service.slug,
                image_full=service.image_full,
                price=str(service.price_tag),
                image_bg=service.image_bg,
                configuration_type=service.configuration_type,
                base_price=service.base_price,
                at_least_one_option_required=service.at_least_one_option_required
            ),
            statistics=ServiceStatistics(
                eta=service.eta,
                completed=service.completed_count,
                feedback_rating="{:.1f}".format(service.feedback_rating),
                boosters_online=BOOSTERS_ONLINE
            ),
            service_configs=[
                ServiceConfigDTOOutput(
                    title=c.title,
                    price=c.price,
                    old_price=c.old_price,
                    description=c.description,
                    id=c.id,
                    extra_data=c.extra_data
                ) for c in service_configs
            ],
            static_content=StaticContent(
                you_will_get=service.static_data.you_will_get_content,
                description=service.static_data.description,
                requirements=service.static_data.requirements
            ),
            range_slider_configs=service.range_options
        )
