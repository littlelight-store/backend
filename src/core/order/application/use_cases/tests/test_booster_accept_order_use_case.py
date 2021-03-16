from unittest.mock import MagicMock

import pytest

from core.order.application.use_cases.booster_accept_order_use_case import (
    BoosterAcceptOrderDTORequest,
    BoosterAcceptOrderUseCase,
)
from core.order.domain.exceptions import OrderIsAlreadyAccepted


@pytest.fixture()
def uc(
    boosters_repository_mock,
    order_objectives_repository_mock
):
    return BoosterAcceptOrderUseCase(
        boosters_repository_mock,
        order_objectives_repository_mock
    )


@pytest.fixture()
def dto(created_order_objective, booster):
    return BoosterAcceptOrderDTORequest(
        order_objective_id=created_order_objective.id,
        booster_user_id=booster.user_id
    )


@pytest.fixture()
def setup_mocks(
    boosters_repository_mock,
    order_objectives_repository_mock,
    booster,
    order_objective_mock
):
    boosters_repository_mock.get_by_user_id = MagicMock(return_value=booster)
    order_objectives_repository_mock.get_by_id = MagicMock(return_value=order_objective_mock)
    order_objectives_repository_mock.save = MagicMock()


@pytest.fixture()
def objective_dont_have_booster(order_objective_mock):
    order_objective_mock.assign_booster = MagicMock()


@pytest.fixture()
def objective_has_booster(order_objective_mock):
    order_objective_mock.assign_booster = MagicMock(side_effect=OrderIsAlreadyAccepted)


def test_positive_booster_accept_order(
    uc,
    dto,
    setup_mocks,
    objective_dont_have_booster,
    order_objectives_repository_mock,
    order_objective_mock,
    booster
):
    uc.execute(dto)

    order_objective_mock.assign_booster.assert_called_once_with(booster.id)
    order_objectives_repository_mock.save.assert_called_once_with(order_objective_mock)


def test_order_already_taken(uc, dto, setup_mocks, objective_has_booster, order_objective_mock, booster):
    with pytest.raises(OrderIsAlreadyAccepted):
        uc.execute(dto)
        order_objective_mock.assign_booster.assert_called_once_with(booster.id)
