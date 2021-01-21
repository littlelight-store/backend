from dependency_injector import providers
from django.apps import AppConfig


class OrdersConfig(AppConfig):
    name = 'orders'
    verbose_name = 'Orders'

    def ready(self):
        from boosting import container
        from orders.repositories import DjangoClientOrderRepository, DjangoOrderObjectiveRepository
        from orders.repositories import DjangoShoppingCartRepository, DjangoShoppingCartItemRepository
        from orders.repositories import DjangoPromoCodeRepository
        from . import tasks

        container.orders.client_orders_repository.override(providers.Factory(DjangoClientOrderRepository))
        container.orders.order_objectives_repository.override(providers.Factory(DjangoOrderObjectiveRepository))

        container.cart.shopping_cart_repository.override(providers.Factory(DjangoShoppingCartRepository))
        container.cart.shopping_cart_items_repository.override(providers.Factory(DjangoShoppingCartItemRepository))

        container.services.promo_code_repository.override(providers.Factory(DjangoPromoCodeRepository))

        container.wire(modules=[tasks])
