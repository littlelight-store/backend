from unittest.mock import Mock

from dependency_injector import providers

import orders.tasks
from core.order.application.use_cases.order_created_notifications import OrderCreatedNotificationsUseCase


def test_task_order_created_notification():
    from boosting import container
    container.wire(modules=[orders.tasks])
    mock = Mock(spec=OrderCreatedNotificationsUseCase)
    with container.orders_uc.order_created_notifications_uc.override(
        providers.Factory(mock)
    ):
        orders.tasks.order_created_notifications('test')
        mock.assert_called_once()
