import pytest


@pytest.fixture()
def db_client_orders(db_order, db_client):
    db_order.client = db_client
    db_order.save()


@pytest.mark.django_db()
def test_list_django_client_orders_by_user(
    repository,
    db_client_orders,
    client_id
):
    res = repository.list_by_user(client_id)
    assert len(res) == 1
