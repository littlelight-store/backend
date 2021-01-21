import pytest

from core.order.domain.order import ClientOrder
from services.repositories import DestinyServiceConfigRepository


@pytest.fixture()
def rep():
    return DestinyServiceConfigRepository()


@pytest.mark.django_db
def test_map_by_client_order(
    rep, database_order_objective,
    service, client_order: ClientOrder,
    service_config
):
    res = rep.map_by_client_order(client_order.id)
    assert res[service.slug][0].id == service_config.id
