from decimal import Decimal

from core.domain.entities.booster import Booster
from core.domain.entities.bungie_profile import DestinyCharacter, DestinyCharacterClass
from core.domain.entities.constants import ConfigurationType
from core.domain.entities.order import Order
from core.domain.entities.service import Service, ServiceConfig
from utils import generate_random_id, generate_random_price, random_chars


def generate_service(**kwargs):
    return Service(
        title='TEST Service',
        slug='test-service',
        booster_percent=10,
        layout_type='customize-progress',
        item_image='',
        at_least_one_option_required=False,
        base_price=20,
        category='pvp',
        configuration_type=ConfigurationType.base_price,
        static_data=None
    )


def generate_service_config():
    return ServiceConfig(
        _id=generate_random_id(),
        title='Test-service-option',
        description='Test description',
        price=Decimal(100),
        old_price=Decimal(120),
        extra_data={}
    )


def generate_character():
    return DestinyCharacter(
        id=generate_random_id(),
        characterId=next(random_chars(12)),
        classType=DestinyCharacterClass.hunter
    )


def generate_order(**kwargs):
    return Order(
        _id=generate_random_id(),
        parent_order_id=generate_random_id(),
        total_price=generate_random_price(),
        booster_price=generate_random_price(),
        service=generate_service(),
        character=generate_character(),
        **kwargs
    )


def generate_booster(**kwargs):
    return Booster(
        _id=generate_random_id(),
        discord_id='test#1234',
        user_id=generate_random_id(),
        username='Stan',
        **kwargs
    )
