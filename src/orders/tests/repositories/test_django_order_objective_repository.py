import pytest

from orders.repositories import DjangoOrderObjectiveRepository


@pytest.fixture()
def repository():
    return DjangoOrderObjectiveRepository()


@pytest.mark.django_db()
def test_list_order_objectives_by_orders(
    repository,
    database_order_objective,
    client_order
):
    list_by_orders = repository.list_by_orders([client_order.id])
    print(list_by_orders)
