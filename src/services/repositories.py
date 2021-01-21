import typing as t
from collections import defaultdict

from django.db.models import Avg, Count, Q

from core.application.repositories.aggregates.main_page_services_repository import MainPageServicesRepository
from core.application.repositories.service_group_tag import ServiceGroupTagRepository
from core.application.repositories.services import (
    ServiceConfigsRepository, ServiceDetailedInfoRepository, ServiceRepository,
)
from core.domain.entities.service import (
    Service, ServiceConfig, ServiceDetailedInfo, ServiceGroupTag, ServicePageStaticData,
    ShortServiceInfo,
)
from core.order.domain.consts import OrderObjectiveStatus
from services.models import Service as ServiceORM, ServiceConfig as ServiceConfigORM, ServiceGroupTagORM


class DestinyServiceTagRepository(ServiceGroupTagRepository):
    def list(self) -> t.List[ServiceGroupTag]:
        res = ServiceGroupTagORM.objects.all()
        return [self._encode_model(d) for d in res]

    def list_with_services(self) -> t.Dict[ServiceGroupTag, t.List[ServiceGroupTag]]:
        pass

    @staticmethod
    def _encode_model(data: ServiceGroupTagORM) -> ServiceGroupTag:
        return ServiceGroupTag(
            name=data.name,
            value=data.value
        )


class DestinyServiceRepository(ServiceRepository):

    def list_by_client_orders(self, client_orders: t.List[str]) -> t.List[Service]:
        res = ServiceORM.objects.filter(
            order_objectives__client_order_id__in=client_orders
        )
        return list(map(self._encode_model, res))

    def list_by_client_order(self, client_order: str) -> t.List[Service]:
        res = ServiceORM.objects.filter(
            order_objectives__client_order_id=client_order
        )
        return list(map(self._encode_model, res))

    def get_by_slug(self, slug: str) -> Service:
        res = ServiceORM.objects.get(slug=slug)
        return self._encode_model(res)

    def list_active(self) -> t.List[Service]:
        res = ServiceORM.objects.filter(is_hidden=False)
        return [self._encode_model(d) for d in res]

    @staticmethod
    def _encode_model(data: ServiceORM) -> Service:
        return Service(
            title=data.title,
            slug=data.slug,
            booster_percent=data.booster_price,
            layout_type=data.option_type,
            category=data.category.slug,
            item_image=data.item_image.url if data.item_image else None,
            ordering=data.ordering,
            layout_options=data.extra_configs,
            image_bg=data.background_image.url if data.background_image else None,
            configuration_type=data.configuration_type,
            base_price=data.base_price,
            at_least_one_option_required=data.at_least_one_option_required,
            static_data=ServicePageStaticData(
                you_will_get_content=data.you_will_get_content,
                requirements=data.static_requirements,
                description=data.static_description
            )
        )


class DestinyServiceConfigRepository(ServiceConfigsRepository):
    def map_by_client_order(self, client_order: str) -> t.Dict[str, t.List[ServiceConfig]]:

        configs: t.List[ServiceConfigORM] = ServiceConfigORM.objects.filter(
            order_objectives__client_order=client_order
        )
        res = defaultdict(list)
        for el in configs:
            res[el.service_id].append(self._encode_model(el))

        return res

    def list_by_client_orders(self, client_orders: t.List[str]) -> t.List[ServiceConfig]:
        objs = ServiceConfigORM.objects.filter(
            order_objectives__client_order__id__in=client_orders
        )
        return list(map(self._encode_model, objs))

    def list_by_service(self, service_slug: str) -> t.List[ServiceConfig]:
        objs = ServiceConfigORM.objects.filter(service=service_slug)
        return list(map(self._encode_model, objs))

    def list_by_shopping_cart_item(self, cart_item_id: str) -> t.List[ServiceConfig]:
        objs = ServiceConfigORM.objects.prefetch_related('cart_items').filter(cart_items__id=cart_item_id)
        return list(map(self._encode_model, objs))

    @staticmethod
    def _encode_model(config: ServiceConfigORM):
        return ServiceConfig(
            title=config.title,
            description=config.description,
            price=config.price,
            old_price=config.old_price,
            _id=config.id,
            extra_data=config.extra_configs_v2
        )


class DjangoMainPageServicesRepository(MainPageServicesRepository):

    def list_main_page_goods(self) -> t.Dict[ServiceGroupTag, t.List[ShortServiceInfo]]:
        objs = ServiceGroupTagORM.objects.prefetch_related('services').all()
        res = {}

        for obj in objs:
            res[ServiceGroupTag(
                value=obj.value,
                name=obj.name
            )] = list(map(self.encode_service, obj.services.filter(is_hidden=False)))

        return res

    @staticmethod
    def encode_service(service: ServiceORM) -> ShortServiceInfo:
        return ShortServiceInfo(
            title=service.title,
            image=service.item_image.url if service.item_image else None,
            slug=service.slug,
            layout_options=service.extra_configs,
            is_hot=service.is_hot,
            is_new=service.is_new
        )


class DjangoServiceDetailedInfoRepository(ServiceDetailedInfoRepository):

    def get_by_slug(self, service_slug: str) -> ServiceDetailedInfo:
        obj = ServiceORM.objects.prefetch_related('order_objectives', 'reviews').annotate(
            completed_count=Count(
                'order_objectives',
                distinct=True,
                filter=Q(
                    order_objectives__status=OrderObjectiveStatus.COMPLETED,
                    order_objectives__client_order__review=None
                )
            ),
            feedbacks_count=Count(
                'reviews',
                distinct=True,
            ),
            feedback_rating_avg=Avg('reviews__rate')
        ).get(
            slug=service_slug,
        )

        print(len(obj.reviews.all()))
        print(obj.feedbacks_count)

        return self._encode_model(
            obj,
            completed_count=obj.completed_count + obj.feedbacks_count,
            feedback_rating=obj.feedback_rating_avg
        )

    @staticmethod
    def _encode_model(
        data: ServiceORM,
        feedback_rating,
        completed_count
    ) -> ServiceDetailedInfo:
        return ServiceDetailedInfo(
            title=data.title,
            slug=data.slug,
            image_bg=data.background_image.url if data.background_image else None,
            image_full=data.item_image.url if data.item_image else None,
            configuration_type=data.configuration_type,
            base_price=data.base_price,
            at_least_one_option_required=data.at_least_one_option_required,
            eta=data.eta,
            feedback_rating=float(feedback_rating) if feedback_rating else 0,
            completed_count=completed_count,
            layout_options=data.extra_configs,
            static_data=ServicePageStaticData(
                you_will_get_content=data.you_will_get_content,
                requirements=data.static_requirements,
                description=data.static_description
            )
        )
