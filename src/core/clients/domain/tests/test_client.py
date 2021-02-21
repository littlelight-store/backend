import datetime as dt
from decimal import Decimal

import pytest

from core.clients.domain.client import Client


@pytest.fixture()
def client_with_cashback(service_client):
    service_client.cashback = Decimal(100)
    return service_client


@pytest.mark.parametrize('value', (99, 100))
def test_has_enough_cashback(client_with_cashback: Client, value):
    assert client_with_cashback.has_enough_cashback(Decimal(value))


def test_not_has_enough_cashback(client_with_cashback: Client):
    assert not client_with_cashback.has_enough_cashback(Decimal(101))


@pytest.fixture()
def notified_client(service_client):
    service_client.last_chat_message_send_at = dt.datetime.utcnow()


@pytest.mark.freeze_time('2020-01-01')
def test_to_early_to_send_notification(service_client):
    service_client.last_chat_message_send_at = (dt.datetime.utcnow() - dt.timedelta(hours=2))

    assert not service_client.can_send_email_chat_notification()


@pytest.mark.freeze_time('2020-01-01')
def test_okay_to_send_notification(service_client):
    service_client.last_chat_message_send_at = (dt.datetime.utcnow() - dt.timedelta(hours=4, minutes=20))

    assert service_client.can_send_email_chat_notification()


@pytest.mark.freeze_time('2020-01-01')
def test_okay_to_send_notification_then_not_ok(service_client):
    service_client.last_chat_message_send_at = (dt.datetime.utcnow() - dt.timedelta(hours=4, minutes=20))

    assert service_client.can_send_email_chat_notification()
    service_client.set_message_sent()
    assert not service_client.can_send_email_chat_notification()
