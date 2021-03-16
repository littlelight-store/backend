import typing as t
from decimal import Decimal

from pydantic import BaseModel

from core.application.dtos.notifications.event_notifications import EventOrderCreatedDTO, EventOrderCreatedOptionDTO
from core.application.repositories import EventNotificationRepository
from core.application.repositories.notifications import OrderCreatedDTO, OrderExecutorsNotificationRepository
from core.application.repositories.services import ServiceConfigsRepository, ServiceRepository
from core.bungie.entities import DestinyCharacter, DestinyBungieProfile
from core.bungie.repositories import DestinyBungieCharacterRepository, DestinyBungieProfileRepository
from core.clients.application.repository import ClientsRepository
from core.clients.domain.client import Client
from core.domain.entities.service import Service, ServiceConfig
from core.order.application.repository import ClientOrderRepository, OrderObjectiveRepository
from core.order.domain.order import ClientOrder, ClientOrderObjective
from core.utils.map_by_key import map_by_key
from notificators.discord import _get_channels_category
from notificators.new_email import DjangoEmailNotificator, NewOrderCreatedNotification


class OrderCreatedNotificationsUseCaseDTOInput(BaseModel):
    client_order_id: str


class OrderCreatedNotificationsUseCase:
    def __init__(
        self,
        event_notifications_repository: EventNotificationRepository,
        client_orders_repository: ClientOrderRepository,
        order_objectives_repository: OrderObjectiveRepository,
        services_repository: ServiceRepository,
        service_configs_repository: ServiceConfigsRepository,
        destiny_bungie_profile_repository: DestinyBungieProfileRepository,
        destiny_character_repository: DestinyBungieCharacterRepository,
        clients_repository: ClientsRepository,
        email_notificator: DjangoEmailNotificator,
        order_executors_repository: OrderExecutorsNotificationRepository
    ):
        self.email_notificator = email_notificator
        self.service_configs_repository = service_configs_repository
        self.services_repository = services_repository
        self.event_notifications_repository = event_notifications_repository
        self.clients_repository = clients_repository
        self.destiny_character_repository = destiny_character_repository
        self.destiny_bungie_profile = destiny_bungie_profile_repository
        self.order_objectives_repository = order_objectives_repository
        self.client_orders_repository = client_orders_repository
        self.order_executors_repository = order_executors_repository

    @staticmethod
    def _make_event_order_created_dto(
        service: Service,
        order: ClientOrder,
        order_objective: ClientOrderObjective,
        selected_options: t.List[ServiceConfig],
        character: DestinyCharacter,
        client: Client,
        profile: DestinyBungieProfile
    ):
        return EventOrderCreatedDTO(
            service_title=service.title,
            total_price=str(order_objective.price),
            platform=order.platform,
            character_class=character.character_class,
            promo_code=order.promo_code,
            options=[EventOrderCreatedOptionDTO(
                description=s.title,
                price=str(s.price)
            ) for s in selected_options],
            user_email=client.email,
            username=profile.username
        )

    @staticmethod
    def services_map(services: t.List[Service]) -> t.Dict[str, Service]:
        data: t.Dict[str, Service] = dict()

        for s in services:
            data[s.slug] = s

        return data

    def send_email(
        self,
        order: ClientOrder,
        order_objectives: t.List[ClientOrderObjective],
        services: t.Dict[str, Service],
        client: Client,
    ):
        self.email_notificator.send_order_created(
            NewOrderCreatedNotification(
                order_number=order.order_id,
                total='${:.2f}'.format(order.total_price),
                user_email=client.email,
                services=[f"{services[s.service_slug].title}" for s in order_objectives],
                platform=order.platform.name
            )
        )

    def send_order_executors_notifications(
        self,
        order: ClientOrder,
        order_objective: ClientOrderObjective,
        selected_options: t.List[ServiceConfig],
        service: Service,
        profile: DestinyBungieProfile
    ):
        dto = OrderCreatedDTO(
            service_title=service.title,
            created_at=order.created_at,
            order_id=order_objective.id,
            selected_services=[EventOrderCreatedOptionDTO(
                description=s.title,
                price=str(s.price)
            ) for s in selected_options],
            platform=order.platform,
            category=_get_channels_category(service.category),
            client_username=profile.username,
            booster_price=order_objective.get_booster_price(Decimal(service.booster_percent))
        )
        self.order_executors_repository.order_created(dto)

    def execute(self, dto: OrderCreatedNotificationsUseCaseDTOInput):
        order = self.client_orders_repository.get_by_id(dto.client_order_id)
        objectives = self.order_objectives_repository.get_by_order(order.id)

        client = self.clients_repository.get_by_id(order.client_id)
        profiles = map_by_key(
            iterable=self.destiny_bungie_profile.list_by_client_order_id(order.id),
            key='membership_id'
        )
        characters = map_by_key(
            self.destiny_character_repository.list_by_client_order_id(order.id),
            'character_id'
        )

        services = self.services_map(self.services_repository.list_by_client_order(order.id))
        service_configs = self.service_configs_repository.map_by_client_order(order.id)

        for obj in objectives:
            service = services.get(obj.service_slug)
            configs = service_configs.get(obj.service_slug, [])

            selected_options = []

            for conf in configs:
                if conf.id in obj.selected_option_ids:
                    selected_options.append(conf)

            profile = profiles.get(obj.destiny_profile_id)
            character = characters.get(obj.destiny_character_id)

            self.event_notifications_repository.new_order_created(
                self._make_event_order_created_dto(
                    service=service,
                    order=order,
                    order_objective=obj,
                    selected_options=selected_options,
                    client=client,
                    profile=profile,
                    character=character
                )
            )
            self.send_order_executors_notifications(
                service=service,
                order=order,
                order_objective=obj,
                selected_options=selected_options,
                profile=profile
            )

        self.send_email(
            order=order,
            order_objectives=objectives,
            services=services,
            client=client
        )


