from core.order.domain.consts import OrderObjectiveStatus


def run():
    from orders.models import Order
    from orders.orm_models import ORMOrderObjective

    orders = []

    for order in Order.objects.filter(is_faked=False):
        orders.append(
            ORMOrderObjective(
                service=order.service,
                status=OrderObjectiveStatus.COMPLETED
            )
        )

    ORMOrderObjective.objects.bulk_create(orders)

