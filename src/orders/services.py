from dependency_injector import containers, providers

from core.application.repositories import NotificationsRepository, OrderRepo
from core.application.repositories.order import BoostersRepo
from core.application.use_cases.assign_booster_to_order import AssignBoosterToOrderUseCase
from core.shopping_cart.application.use_cases.add_to_shopping_cart import AddItemToShoppingCartUseCase
from core.shopping_cart.application.use_cases.apply_promo import ApplyPromoUseCase
from core.shopping_cart.application.use_cases.cart_payed import CartPayedUseCase
from core.shopping_cart.application.use_cases.list_shopping_cart import ListShoppingCartUseCase
from core.shopping_cart.application.use_cases.remove_cart_item import RemoveCartItemUseCase
from infrastructure.injectors.service import DestinyServiceInjectors
from notificators.email import EmailNotificator
from notificators.telegram import TelegramNotificator
from orders.repositories import (
    DjangoClientOrderRepository, DjangoOrderObjectiveRepository, DjangoPromoCodeRepository,
    DjangoShoppingCartItemRepository,
    DjangoShoppingCartRepository,
)
from orders.repository import DjangoOrderRepository
from profiles.repository import (
    DjangoBoostersRepository, DjangoClientRepository, DjangoDestinyBungieProfileRepository,
    DjangoDestinyCharacterRepository, DjangoProfileCredentialsRepository
)


class NotificationService(containers.DeclarativeContainer):
    event_notifications_repo = providers.Singleton(TelegramNotificator)
    client_notifications_repo = providers.Singleton(EmailNotificator)

    notifications_repo = providers.Factory(
        NotificationsRepository,
        event_repository=event_notifications_repo,
        client_notification_repository=client_notifications_repo,
    )


class ClientServices(containers.DeclarativeContainer):
    clients_repository = providers.Singleton(DjangoClientRepository)
    client_credentials_repository = providers.Singleton(DjangoProfileCredentialsRepository)


class BungieProfilesService(containers.DeclarativeContainer):
    destiny_bungie_profile_repository = providers.Singleton(DjangoDestinyBungieProfileRepository)
    destiny_character_repository = providers.Singleton(DjangoDestinyCharacterRepository)


class ShoppingCartService(containers.DeclarativeContainer):
    shopping_cart_repository = providers.Singleton(
        DjangoShoppingCartRepository)
    shopping_cart_items_repository = providers.Singleton(
        DjangoShoppingCartItemRepository)
    client_order_repository = providers.Singleton(
        DjangoClientOrderRepository)
    order_objective_repository = providers.Singleton(
        DjangoOrderObjectiveRepository
    )
    promo_code_repository = providers.Singleton(
        DjangoPromoCodeRepository
    )

    add_item_uc = providers.Factory(
        AddItemToShoppingCartUseCase,
        shopping_cart_repository=shopping_cart_repository,
        shopping_cart_items_repository=shopping_cart_items_repository,
        destiny_bungie_profile_repository=BungieProfilesService.destiny_bungie_profile_repository,
        destiny_character_repository=BungieProfilesService.destiny_character_repository,
        service_repository=DestinyServiceInjectors.service_rep,
        service_configs_repository=DestinyServiceInjectors.service_configs_rep,
        promo_code_repository=promo_code_repository
    )

    list_items_uc = providers.Factory(
        ListShoppingCartUseCase,
        shopping_cart_repository=shopping_cart_repository,
        shopping_cart_items_repository=shopping_cart_items_repository,
        destiny_bungie_profile_repository=BungieProfilesService.destiny_bungie_profile_repository,
        destiny_character_repository=BungieProfilesService.destiny_character_repository,
        service_repository=DestinyServiceInjectors.service_rep,
        service_configs_repository=DestinyServiceInjectors.service_configs_rep,
        promo_code_repository=promo_code_repository
    )

    cart_payed_uc = providers.Factory(
        CartPayedUseCase,
        cart_repository=shopping_cart_repository,
        cart_item_repository=shopping_cart_items_repository,
        order_repository=client_order_repository,
        clients_repository=ClientServices.clients_repository,
        order_objective_repository=order_objective_repository,
        service_repository=DestinyServiceInjectors.service_rep,
        service_configs_repository=DestinyServiceInjectors.service_configs_rep,
        promo_code_repository=promo_code_repository,
        destiny_bungie_profile_repository=BungieProfilesService.destiny_bungie_profile_repository,
        destiny_bungie_characters_repository=BungieProfilesService.destiny_character_repository,
        profile_credentials_repository=ClientServices.client_credentials_repository
    )
    remove_cart_item_uc = providers.Factory(
        RemoveCartItemUseCase,
        shopping_cart_items_repository=shopping_cart_items_repository,
        cart_repository=shopping_cart_repository,
        service_repository=DestinyServiceInjectors.service_rep,
        service_configs_repository=DestinyServiceInjectors.service_configs_rep,
        promo_code_repository=promo_code_repository
    )

    apply_promo_uc = providers.Factory(
        ApplyPromoUseCase,
        shopping_cart_repository=shopping_cart_repository,
        shopping_cart_items_repository=shopping_cart_items_repository,
        service_repository=DestinyServiceInjectors.service_rep,
        service_configs_repository=DestinyServiceInjectors.service_configs_rep,
        promo_code_repository=promo_code_repository
    )


class AssignBoosterService(containers.DeclarativeContainer):
    db_order_repo = providers.Factory(DjangoOrderRepository)
    order_repo = providers.Factory(OrderRepo, db_repo=db_order_repo)
    db_boosters_repo = providers.Factory(DjangoBoostersRepository)
    boosters_repo = providers.Factory(BoostersRepo, db_repo=db_boosters_repo)

    use_case = providers.Factory(
        AssignBoosterToOrderUseCase,
        order_repo=order_repo,
        boosters_repo=boosters_repo,
        notification_repo=NotificationService.notifications_repo
    )
