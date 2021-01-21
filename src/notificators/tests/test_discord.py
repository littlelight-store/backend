from decimal import Decimal
from unittest.mock import Mock, MagicMock

import pytest
from discord import Webhook

from core.domain.entities.order import ParentOrder, Order
from core.domain.entities.service import Service
from notificators.discord import DiscordNotificator, MessageBuilder, BOT_NAME
from orders.parse_product_options import TemplateRepresentation


@pytest.fixture
def notificator():
    return DiscordNotificator(
        message_builder=Mock(spec=MessageBuilder),
        _web_hook_factory=MagicMock(return_value=Mock(spec=Webhook))
    )


@pytest.fixture
def parent_order():
    mock = MagicMock(spec=ParentOrder)
    mock.platform = Mock()
    return mock


@pytest.fixture
def order():
    order = MagicMock(spec=Order)

    order.id = 443
    order.service = MagicMock(Service)
    order.service.title = 'Test'
    order.service.category = 'pvp'
    order.booster_price = Decimal(20)
    order.service.options_representation = [
        TemplateRepresentation(
            description='Service config — 1',
            price='123'
        ),
        TemplateRepresentation(
            description='Service config — 2',
            price='123'
        ),
    ]
    return order


def test_message_builder(order, parent_order):
    result = MessageBuilder().set_params(order, parent_order).execute()
    assert result.content == ''

    # Field with booster price is +1
    # Field with accept process description is +1
    assert len(result.embed.fields) == len(order.service.options_representation) + 2
    assert order.service.title in result.embed.title
    assert str(order.id) in result.embed.title


def test_send_notificator_new_order_message(
    notificator: pytest.fixture,
    parent_order: pytest.fixture,
    order: pytest.fixture
):
    result_mock = Mock()

    result_mock.content = Mock()
    result_mock.embed = Mock()

    notificator.message_builder.return_value.set_params.return_value.execute.return_value = result_mock
    parent_order.orders = [order]

    notificator.order_created(parent_order)

    notificator._web_hook_factory().send.assert_called_with(
        result_mock.content, username=BOT_NAME, embed=result_mock.embed
    )
