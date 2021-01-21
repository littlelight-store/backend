import pytest

from core.order.domain.order import ClientOrder
from services.repositories import DestinyServiceRepository


@pytest.fixture()
def rep():
    return DestinyServiceRepository()


@pytest.mark.django_db
def test_list_by_client_order(
    rep, database_order_objective,
    service, client_order: ClientOrder
):
    data = rep.list_by_client_order(client_order.id)

    assert len(data) == 1
    assert data[0].slug == service.slug
