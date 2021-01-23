from unittest.mock import MagicMock, Mock

import pytest

from core.application.repositories import EventNotificationRepository
from core.application.repositories.services import ServiceConfigsRepository, ServiceRepository
from core.bungie.repositories import DestinyBungieCharacterRepository, DestinyBungieProfileRepository
from core.clients.application.repository import ClientsRepository
from core.order.application.repository import ClientOrderRepository, OrderObjectiveRepository
from core.order.application.use_cases.order_created_notifications import (
    OrderCreatedNotificationsUseCase,
    OrderCreatedNotificationsUseCaseDTOInput,
)
from notificators.new_email import DjangoEmailNotificator


@pytest.fixture()
def uc():
    return OrderCreatedNotificationsUseCase(
        event_notifications_repository=Mock(spec=EventNotificationRepository),
        client_orders_repository=Mock(spec=ClientOrderRepository),
        order_objectives_repository=Mock(spec=OrderObjectiveRepository),
        services_repository=Mock(spec=ServiceRepository),
        service_configs_repository=Mock(spec=ServiceConfigsRepository),
        destiny_bungie_profile_repository=Mock(spec=DestinyBungieProfileRepository),
        destiny_character_repository=Mock(spec=DestinyBungieCharacterRepository),
        clients_repository=Mock(spec=ClientsRepository),
        email_notificator=Mock(spec=DjangoEmailNotificator)
    )


@pytest.fixture()
def setup_uc(
    uc,
    client_order,
    created_order_objective,
    service,
    created_character,
    created_profile,
    service_config,
    service_client
):
    uc.client_orders_repository.get_by_id = MagicMock(
        return_value=client_order
    )
    uc.order_objectives_repository.get_by_order = MagicMock(
        return_value=[created_order_objective]
    )
    uc.services_repository.list_by_client_order = MagicMock(
        return_value=[service]
    )
    uc.service_configs_repository.map_by_client_order = MagicMock(
        return_value={service.slug: [service_config]}
    )
    uc.destiny_bungie_profile.list_by_client_order_id = MagicMock(
        return_value=[created_profile]
    )
    uc.destiny_character_repository.list_by_client_order_id = MagicMock(
        return_value=[created_character]
    )
    uc.clients_repository.get_by_id = MagicMock(
        return_value=service_client
    )
    yield uc


def test_send_order_created_message(
    setup_uc,
    created_order_objective,
    service_config
):
    created_order_objective.selected_option_ids = [service_config.id]
    dto = OrderCreatedNotificationsUseCaseDTOInput(
        client_order_id='some-id'
    )

    setup_uc.execute(dto)

    setup_uc.client_orders_repository.get_by_id.assert_called_with(dto.client_order_id)
