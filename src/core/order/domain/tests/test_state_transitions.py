from unittest.mock import Mock

import pytest

from core.order.domain.consts import OrderObjectiveStatus
from core.order.domain.order_states import OrderObjectiveStateMachineMixin, get_state_machine


@pytest.fixture()
def notifier_mock():
    return Mock(spec=OrderObjectiveStateMachineMixin)


@pytest.fixture()
def order_objective_state_machine_fixture(notifier_mock):
    return get_state_machine(notifier_mock)


def test_transition_from_created(order_objective_state_machine_fixture, notifier_mock):
    assert notifier_mock.is_CREATED()
    notifier_mock.processing()
    assert notifier_mock.is_PROCESSING()


def test_transition_booster_assigned(order_objective_state_machine_fixture, notifier_mock):
    order_objective_state_machine_fixture.set_state(OrderObjectiveStatus.PROCESSING)
    assert notifier_mock.is_PROCESSING()
    notifier_mock.booster_assigned()
    assert notifier_mock.is_AWAITING_BOOSTER()
