from core.order.application.repository import MQEventsRepository


class CeleryEventsRepository(MQEventsRepository):

    def new_message_push_send(self, receiver_id: int, message: str):
        from orders.tasks import new_chat_message
        new_chat_message.delay(client_id=receiver_id, message=message)

    def new_order_created(self, client_order_id: str):
        from orders.tasks import order_created_notifications
        order_created_notifications.delay(client_order_id=client_order_id)

    def new_message_send(self, user_email: str, from_message: str):
        from orders.tasks import chat_message_unread
        chat_message_unread.delay(
            user_email=user_email,
            from_message=from_message
        )

