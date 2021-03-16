import datetime as dt
from unittest.mock import MagicMock

import pytest

from core.boosters.domain.entities import Booster
from core.bungie.entities import DestinyBungieProfile
from core.bungie.test_utils import generate_destiny_bungie_profile, generate_destiny_character
from core.clients.domain.client import Client
from core.domain.entities.tests.utils import generate_service, generate_service_config
from core.order.test_utils import generate_client_order, generate_order_objectives
from orders.orm_models import ORMClientOrder, ORMOrderObjective
from orders.repositories import DjangoClientOrderRepository
from profiles.constants import CharacterClasses, Membership
from profiles.models import User
from profiles.orm_models import ORMDestinyBungieCharacter, ORMDestinyBungieProfile
from services.models import Category as CategoryORM, Service as ServiceORM, ServiceConfig as ServiceConfigORM
from utils import generate_random_id


@pytest.fixture()
def client_order():
    return generate_client_order()


@pytest.fixture()
def order_objective(client_order, service, destiny_character, destiny_profile, client_id):
    def func(**kwargs):
        profile = destiny_profile()
        data = dict(
            client_order=client_order,
            service=service,
            destiny_character=destiny_character(destiny_profile=profile),
            destiny_profile=profile,
            client_id=client_id
        )
        data.update(kwargs)

        return generate_order_objectives(**data)
    return func


@pytest.fixture()
def destiny_profile():
    def func(membership_type: Membership = Membership.BattleNET):
        return generate_destiny_bungie_profile(membership_type=membership_type)
    return func


@pytest.fixture()
def obj_destiny_profile(destiny_profile) -> DestinyBungieProfile:
    return destiny_profile()


@pytest.fixture()
def created_profile(destiny_profile):
    return destiny_profile()


@pytest.fixture()
def created_character(created_profile, destiny_character):
    return destiny_character(destiny_profile=created_profile)


@pytest.fixture()
def created_order_objective(order_objective, created_character, created_profile):
    return order_objective(
        destiny_character=created_character,
        destiny_profile=created_profile
    )


@pytest.fixture()
def db_destiny_profile(obj_destiny_profile: DestinyBungieProfile):
    return ORMDestinyBungieProfile.objects.create(
        membership_id=obj_destiny_profile.membership_id,
        membership_type=obj_destiny_profile.membership_type,
        username=obj_destiny_profile.username
    )


@pytest.fixture()
def destiny_character():
    def func(
        destiny_profile: DestinyBungieProfile,
        character_class: CharacterClasses = CharacterClasses.warlock,
    ):
        return generate_destiny_character(character_class=character_class, destiny_profile=destiny_profile)
    return func


@pytest.fixture()
def obj_destiny_character(obj_destiny_profile, destiny_character):
    return destiny_character(
        obj_destiny_profile
    )


@pytest.fixture()
def db_destiny_character(obj_destiny_character, db_destiny_profile):
    return ORMDestinyBungieCharacter.objects.create(
        bungie_profile=db_destiny_profile,
        character_id=obj_destiny_character.character_id,
        character_class=obj_destiny_character.character_class.value
    )


@pytest.fixture()
def service():
    return generate_service()


@pytest.fixture()
def service_config():
    return generate_service_config()


@pytest.fixture()
def service_client():
    return Client(
        _id=42,
        email='test@test.ru',
        discord='#TEST',
        username='Some username'
    )


@pytest.fixture()
def db_category():
    category = CategoryORM.objects.create(
        name='Some-name',
        slug='pvp'
    )
    return category


@pytest.fixture()
def db_service(service, db_category):
    _db_service = ServiceORM.objects.create(
        category=db_category, title=service.title,
        option_type="single",
        slug=service.slug
    )
    return _db_service


@pytest.fixture()
def db_service_configs(db_service, service_config):
    service_config = ServiceConfigORM.objects.create(
        service=db_service,
        title=service_config.title,
        description=service_config.description,
        price=service_config.price,
        id=service_config.id
    )
    return service_config


@pytest.fixture()
def db_order(client_order):
    order = ORMClientOrder.objects.create(
        id=client_order.id,
        payment_id=client_order.payment_id,
        platform_id=client_order.platform.value,
        created_at=client_order.created_at,
        order_status_changed_at=client_order.order_status_changed_at,
        order_status=client_order.order_status
    )

    return order


@pytest.fixture()
def database_order_objective(
    db_order,
    db_category,
    db_service,
    db_service_configs,
    db_destiny_profile,
    db_destiny_character
):
    obj = ORMOrderObjective.objects.create(
        client_order=db_order,
        price=100,
        service=db_service,
        status_changed_at=dt.datetime.now(),
        destiny_profile=db_destiny_profile,
        destiny_character=db_destiny_character
    )
    obj.selected_options.add(db_service_configs)


@pytest.fixture()
def repository():
    return DjangoClientOrderRepository()


@pytest.fixture()
def client_id():
    return generate_random_id()


@pytest.fixture()
def client(client_id):
    return Client(
        email='some-tets-client-email@gmail.com',
        _id=client_id,
        username='Test username'
    )


@pytest.fixture()
def booster():
    return Booster(
        _id=123,
        user_id=321,
        rating=4.5,
        avatar='',
        username='Test booster username'
    )


@pytest.fixture()
def db_client(client: Client) -> User:
    return User.objects.create(
        username=client.email,
        id=client.id,
        email=client.email,
        is_booster=False
    )


@pytest.fixture()
def boosters_repository_mock():
    from core.boosters.application.repository import BoostersRepository
    return MagicMock(spec=BoostersRepository)


@pytest.fixture()
def clients_repository_mock():
    from core.clients.application.repository import ClientsRepository
    return MagicMock(spec=ClientsRepository)


@pytest.fixture()
def order_objectives_repository_mock():
    from core.order.application.repository import OrderObjectiveRepository
    return MagicMock(spec=OrderObjectiveRepository)


@pytest.fixture()
def order_objective_mock():
    from core.order.domain.order import ClientOrderObjective
    return MagicMock(spec=ClientOrderObjective)
