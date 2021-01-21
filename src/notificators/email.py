from core.application.repositories.notifications import ClientNotificationRepository
from core.domain.entities.client import Client
from core.domain.entities.order import ParentOrder
from orders.tasks import order_created


class EmailNotificator(ClientNotificationRepository):

    def order_created(self, parent_order: ParentOrder, client: Client):
        order_created.delay(
            user_email=client.email,
            order_number=parent_order.invoice_number,
            username=parent_order.bungie_profile.username,
            platform=parent_order.platform.name,
            order_info=[
                dict(
                    title=o.service.title,
                    price=str(o.total_price),
                    promo=parent_order.promo.code if parent_order.promo else None,
                    options=[option.dict() for option in o.service.options_representation],
                    link=o.service.product_link,
                    character_class=o.character.character_class.name
                ) for o in parent_order.orders
            ],
            total=str(parent_order.total_price)
        )
