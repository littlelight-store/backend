from core.order.domain.consts import OrderObjectiveStatus


def test_order_set_processing(created_order_objective):
    last_updated_date = created_order_objective.status_changed_at
    assert created_order_objective.status != OrderObjectiveStatus.PROCESSING
    created_order_objective.processing()
    assert created_order_objective.status == OrderObjectiveStatus.PROCESSING
    assert created_order_objective.status_changed_at != last_updated_date
