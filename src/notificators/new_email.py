import typing as t

from pydantic import BaseModel


class NewOrderCreatedNotification(BaseModel):
    order_number: str
    total: str
    services: t.List[str]
    user_email: str
    platform: str


class DjangoEmailNotificator:

    @staticmethod
    def send_order_created(data: NewOrderCreatedNotification):
        from orders.tasks import new_order_created

        new_order_created.delay(
            total_price=data.total,
            order_id=data.order_number,
            services=data.services,
            user_email=data.user_email,
            platform=data.platform
        )
