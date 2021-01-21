from unittest.mock import Mock, MagicMock

import pytest

from core.application.repositories import OrderRepo, NotificationsRepository
from core.application.repositories.order import BoostersRepo
from core.application.use_cases.assign_booster_to_order import AssignBoosterToOrderUseCase
from core.domain.entities.tests.utils import generate_booster, generate_order
from orders.enum import OrderStatus


@pytest.fixture
def assign_booster_uc():
    return AssignBoosterToOrderUseCase(
        order_repo=Mock(spec=OrderRepo),
        boosters_repo=Mock(spec=BoostersRepo),
        notification_repo=Mock(spec=NotificationsRepository)
    )


@pytest.fixture
def order_id():
    return 1


@pytest.fixture
def booster_discord():
    return 'test#1234'


@pytest.mark.asyncio()
async def test_assign_booster_to_order(
    assign_booster_uc: AssignBoosterToOrderUseCase,
    order_id,
    booster_discord
):
    booster = generate_booster()
    order = generate_order()

    assign_booster_uc.boosters_repo.get_by_discord = MagicMock(return_value=booster)
    assign_booster_uc.order_repo.get_order = MagicMock(return_value=order)

    await assign_booster_uc.set_params(order_id, booster_discord).execute()

    assign_booster_uc.boosters_repo.get_by_discord.assert_called_with(booster_discord)
    assign_booster_uc.order_repo.get_order.assert_called_with(order_id)

    assert order.booster_user_id == booster.user_id
    assert order.status == OrderStatus.waiting_for_booster

    assign_booster_uc.order_repo.update_order.assert_called_with(order)
