from dependency_injector import containers, providers

from core.shopping_cart.application.use_cases.add_to_shopping_cart import AddItemToShoppingCartUseCase
from core.shopping_cart.application.use_cases.apply_promo import ApplyPromoUseCase
from core.shopping_cart.application.use_cases.list_shopping_cart import ListShoppingCartUseCase
from core.shopping_cart.application.use_cases.remove_cart_item import RemoveCartItemUseCase
from infrastructure.injectors.service import DestinyServiceInjectors
from orders.repositories import (
    DjangoClientOrderRepository, DjangoOrderObjectiveRepository, DjangoPromoCodeRepository,
    DjangoShoppingCartItemRepository,
    DjangoShoppingCartRepository,
)
from profiles.repository import (
    DjangoClientRepository, DjangoDestinyBungieProfileRepository,
    DjangoDestinyCharacterRepository, DjangoProfileCredentialsRepository
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
