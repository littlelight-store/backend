import typing as t

from profiles.constants import Membership
from .domain.order import ClientOrder, ClientOrderObjective
from ..bungie.entities import DestinyBungieProfile, DestinyCharacter
from ..domain.entities.service import Service


def generate_client_order(**kwargs):
    data = {
        'total_price': 100,
        'cart_id': '123',
        'client_id': 12,
        'payment_id': 'some-payment-id',
        'comment': '',
        'platform': Membership.BattleNET,
        'promo_code': None,
        **kwargs,
    }
    return ClientOrder.create(
        **data
    )


def generate_order_objectives(
    client_order: ClientOrder,
    service: Service,
    destiny_character: DestinyCharacter,
    destiny_profile: DestinyBungieProfile,
    selected_option_ids: t.List[int] = list,
    range_options: t.Optional[dict] = None,
    **kwargs
):
    data = dict(
        client_order_id=client_order.id,
        service_slug=service.slug,
        destiny_character_id=destiny_character.id,
        destiny_profile_id=destiny_profile.id,
        selected_option_ids=selected_option_ids,
        range_options=range_options,
        **kwargs
    )

    return ClientOrderObjective.create(**data)
