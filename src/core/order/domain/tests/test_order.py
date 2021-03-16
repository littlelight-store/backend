import pytest

from core.order.domain.consts import OrderObjectiveStatus
from core.order.domain.exceptions import OrderIsAlreadyAccepted


def test_order_set_processing(created_order_objective):
    last_updated_date = created_order_objective.status_changed_at
    assert created_order_objective.status != OrderObjectiveStatus.PROCESSING
    created_order_objective.processing()
    assert created_order_objective.status == OrderObjectiveStatus.PROCESSING
    assert created_order_objective.status_changed_at != last_updated_date


def test_assign_booster(created_order_objective, booster):
    created_order_objective.booster_id = None

    created_order_objective.assign_booster(booster.id)
    assert created_order_objective.status == OrderObjectiveStatus.AWAITING_BOOSTER
    assert created_order_objective.booster_id == booster.id


def test_assign_booster_already_assigned(created_order_objective, booster):
    created_order_objective.booster_id = booster.id

    with pytest.raises(OrderIsAlreadyAccepted):
        created_order_objective.assign_booster(booster.id)


