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


class DashboardChatNewMessage(BaseModel):
    from_: str
    user_email: str


class PausedOrder(BaseModel):
    booster_username: str
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

    @staticmethod
    def send_new_chat_message(data: DashboardChatNewMessage):
        from orders.tasks import chat_message_unread
        chat_message_unread.delay(
            from_message=data.from_,
            user_email=data.user_email,
        )

    @staticmethod
    def send_paused_order(data: PausedOrder):
        from orders.tasks import paused_order
        paused_order.delay(
            user_email=data.user_email,
            booster_username=data.booster_username,
        )

    @staticmethod
    def required_2fa_code(user_email):
        from orders.tasks import required_2fa_code
        required_2fa_code.delay(
            user_email=user_email,
        )

    @staticmethod
    def invalid_credentials(email):
        from orders.tasks import invalid_credentials
        invalid_credentials.delay(
            user_email=email
        )
