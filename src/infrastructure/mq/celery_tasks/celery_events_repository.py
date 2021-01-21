from core.order.application.repository import MQEventsRepository


class CeleryEventsRepository(MQEventsRepository):

    def new_order_created(self, client_order_id: str):
        from orders.tasks import order_created_notifications

        order_created_notifications.delay(client_order_id=client_order_id)

    def send_email_order_details(self, client_order_id: str):
        from orders.tasks import order_created_notifications

        order_created_notifications.delay(client_order_id=client_order_id)
