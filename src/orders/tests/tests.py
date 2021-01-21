import datetime as dt

from django.core import mail
from freezegun import freeze_time
from parameterized import parameterized
from rest_framework.test import APITestCase

from orders.enum import OrderStatus
from orders.models import ChatMessage, Order
from orders.tasks import accept_pending_orders
from profiles.models import BungieID, User
from services.models import Category, PromoCode, Service

created_before_midnight = dt.datetime(year=2018, month=1, day=1, hour=0, minute=0)
created_at_midnight = dt.datetime(year=2019, month=1, day=1, hour=0, minute=0)


class ChatMessageLatestSelected(APITestCase):
    def setUp(self):
        Order.objects.create(total_price=100)
        latest_order = Order.objects.create(total_price=5)

        ChatMessage.objects.create(
            order=latest_order,
            msg="test",
            created_at=created_before_midnight,
            is_seen=True,
            role="client",
        )
        ChatMessage.objects.create(
            order=latest_order,
            msg="test",
            created_at=created_at_midnight,
            is_seen=False,
            role="client",
        )

    @freeze_time("2019-01-01 00:16:34", tz_offset=0)
    def test_chat_message_unread_selected(self):
        ChatMessage.objects.update(role="client")
        res = Order.get_order_with_last_unread_messages_later_than(5)

        self.assertEqual(len(res), 1)
        order = res[0]

        self.assertEqual(order.total_price, 5)

    @freeze_time("2019-01-01 00:16:34", tz_offset=0)
    def test_chat_all_messages_old_and_unread(self):
        ChatMessage.objects.update(role="client", created_at=created_before_midnight)
        res = Order.get_order_with_last_unread_messages_later_than(5)

        self.assertEqual(len(res), 1)
        order = res[0]

        self.assertEqual(order.total_price, 5)

    @freeze_time("2019-01-01 00:16:34", tz_offset=0)
    def test_chat_all_messages_old_and_seen(self):
        ChatMessage.objects.update(created_at=created_before_midnight, is_seen=True)
        res = Order.get_order_with_last_unread_messages_later_than(5)

        self.assertEqual(len(res), 0)

    @freeze_time("2019-01-01 00:16:34", tz_offset=0)
    def test_chat_message_seen_not_selected(self):
        ChatMessage.objects.update(is_seen=True)
        res = Order.get_order_with_last_unread_messages_later_than(5)

        self.assertEqual(len(res), 0)

    @freeze_time("2019-01-01 00:16:34", tz_offset=0)
    def test_message_was_already_send(self):
        ChatMessage.objects.update(role="booster")
        Order.objects.filter(total_price=5).update(message_sent_to_booster=True)
        res = Order.get_order_with_last_unread_messages_later_than(5)

        self.assertEqual(len(res), 0)

    @freeze_time("2019-01-01 00:16:34", tz_offset=0)
    def test_message_was_already_send_because_of_eldest_message(self):
        created_just_after = dt.datetime(year=2019, month=1, day=1, hour=0, minute=16)

        latest_order = Order.objects.get(total_price=5)

        ChatMessage.objects.create(
            order=latest_order,
            msg="test",
            created_at=created_just_after,
            is_seen=False,
        )

        ChatMessage.objects.update(role="booster")

        res = Order.get_order_with_last_unread_messages_later_than(5)

        self.assertEqual(len(res), 1)

    @freeze_time("2019-01-01 00:16:34", tz_offset=0)
    def test_message_was_already_send_to_both(self):
        Order.objects.filter(total_price=5).update(
            message_sent_to_booster=True, message_sent_to_client=True
        )
        res = Order.get_order_with_last_unread_messages_later_than(5)

        self.assertEqual(len(res), 0)

    @freeze_time("2019-01-01 00:16:34", tz_offset=0)
    def test_chat_message_unread_not_yet_selected(self):
        res = Order.get_order_with_last_unread_messages_later_than(25)

        self.assertEqual(len(res), 0)


class OrderModelStatusValueHasChangedMutations(APITestCase):
    def setUp(self):
        booster_user = User.objects.create_user("email", "email@email.ru", "pass")
        category = Category.objects.create(name="test")
        service = Service.objects.create(
            category=category, title="any", option_type="single"
        )
        bungie_profile = BungieID.objects.create(
            owner=booster_user, membership_id="123", membership_type=3
        )
        Order.objects.create(
            total_price=100, bungie_profile=bungie_profile, service=service,
            layout_options={}
        )

    def test_taken_at_change_to_booster_assigned(self):
        order = Order.objects.get()
        order.status = OrderStatus.attempt_authorization.value
        order.save()

        order = Order.objects.get()
        self.assertNotEqual(order.taken_at, None)

    @parameterized.expand(
        [
            [OrderStatus.two_factor_code_required.value, "2FA code required"],
            [OrderStatus.cant_sign_in.value, "Wrong account information!"],
            [OrderStatus.pending_approval.value, "Your order has been completed"],
        ]
    )
    def test_mail_sent_on_corresponding_change(self, status, mail_subject):
        order = Order.objects.get()
        order.status = status
        order.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, mail_subject)


class CalculatePromoCodePrice(APITestCase):
    def setUp(self):
        PromoCode.objects.create(code="test", discount=10)

    @parameterized.expand(
        [[100, 90], [200, 180], [10, 9],]
    )
    def test_price_calculated_correctly(self, original_price, result_price):
        code = PromoCode.objects.get(code="test")

        result = code.calculate_discount_for_price(original_price)
        self.assertEqual(result, result_price)


class TestAcceptPendingOrdersJob(APITestCase):
    def setUp(self):
        Order.objects.create(total_price=100, layout_options={})

    @freeze_time("2019-01-03 00:00:00", tz_offset=0)
    def test_old_order_state_changed(self):
        order = Order.objects.get()
        order.created_at = "2019-01-03 00:00:00"
        order.complete_at = "2019-01-01 00:00:00"
        order.status = OrderStatus.pending_approval.value
        order.save()

        accept_pending_orders()

        order = Order.objects.get()
        self.assertEqual(order.status, OrderStatus.is_complete.value)
