import typing as t

from pydantic import BaseModel


class NewOrderCreatedNotification(BaseModel):
    order_number: str
    total: str
    services: t.List[str]
    user_email: str
    platform: str


class PendingApprovalNotification(BaseModel):
    services: t.List[str]
    user_email: str


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

    @staticmethod
    def send_pending_approval(data: PendingApprovalNotification):
        from orders.tasks import pending_approval

        pending_approval.delay(
            services=data.services,
            user_email=data.user_email,
        )
