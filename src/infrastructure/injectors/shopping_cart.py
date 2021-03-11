from dependency_injector import containers, providers

from core.shopping_cart.application.repository import ShoppingCartItemRepository, ShoppingCartRepository
from core.shopping_cart.application.use_cases.cart_payed import CartPayedUseCase


class ShoppingCartContainer(containers.DeclarativeContainer):
    shopping_cart_repository = providers.ExternalDependency(ShoppingCartRepository)
    shopping_cart_items_repository = providers.ExternalDependency(ShoppingCartItemRepository)


class ShoppingCartUseCases(containers.DeclarativeContainer):

    services = providers.DependenciesContainer()
    bungie = providers.DependenciesContainer()
    clients = providers.DependenciesContainer()
    orders = providers.DependenciesContainer()
    cart = providers.DependenciesContainer()
    celery_events_repository = providers.DependenciesContainer()
    discord_notificator = providers.Dependency()

    cart_payed_uc = providers.Factory(
        CartPayedUseCase,
        cart_repository=cart.shopping_cart_repository,
        cart_item_repository=cart.shopping_cart_items_repository,
        order_repository=orders.client_orders_repository,
        clients_repository=clients.clients_repository,
        order_objective_repository=orders.order_objectives_repository,
        service_repository=services.service_rep,
        service_configs_repository=services.service_configs_rep,
        promo_code_repository=services.promo_code_repository,
        destiny_bungie_profile_repository=bungie.profiles_repository,
        profile_credentials_repository=clients.clients_credentials_repository,
        events_repository=celery_events_repository.repository,
        order_executors_repository=discord_notificator
    )
