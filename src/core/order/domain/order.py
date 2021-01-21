import datetime as dt
import enum
import typing as t
from decimal import Decimal

from core.boosters.domain.types import BoosterId
from core.domain.utils import generate_id
from core.order.domain.consts import OrderObjectiveStatus
from core.order.domain.order_states import OrderObjectiveStateMachineMixin
from profiles.constants import Membership


class ClientOrderStatus(str, enum.Enum):
    AWAIT_PAYMENT = 'AWAIT_PAYMENT'
    PAYED = 'PAYED'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)


class ClientOrderObjective(OrderObjectiveStateMachineMixin):
    def __init__(
        self,
        _id: str,

        client_order_id: str,
        service_slug: str,

        destiny_character_id: str,
        destiny_profile_id: str,

        selected_option_ids: t.List[int],
        range_options: t.Optional[dict],

        price: Decimal,
        status: OrderObjectiveStatus,
        status_changed_at: dt.datetime,
        booster_id: t.Optional[BoosterId] = None,
    ):
        self.destiny_profile_id = destiny_profile_id
        self.destiny_character_id = destiny_character_id
        self.id = _id
        self.client_order_id = client_order_id
        self.service_slug = service_slug
        self.selected_option_ids = selected_option_ids
        self.price = price
        self.booster_id = booster_id
        self.status = status
        self.status_changed_at = status_changed_at
        self.range_options = range_options

    @classmethod
    def create(
        cls,
        client_order_id: str,
        service_slug: str,

        destiny_character_id: str,
        destiny_profile_id: str,

        selected_option_ids: t.List[int],
        range_options: t.Optional[dict],

        price: Decimal = 0,

    ):
        return cls(
            _id=generate_id(),

            client_order_id=client_order_id,
            service_slug=service_slug,

            destiny_character_id=destiny_character_id,
            destiny_profile_id=destiny_profile_id,

            selected_option_ids=selected_option_ids,
            range_options=range_options,

            price=price,
            status=OrderObjectiveStatus.CREATED,
            status_changed_at=dt.datetime.utcnow()
        )


class ClientOrder:
    objectives: t.List[ClientOrderObjective] = []

    def __init__(
        self,
        total_price: Decimal,
        order_id: str,
        client_id: int,
        payment_id: str,
        _id: str,
        created_at: dt.datetime,
        order_status: ClientOrderStatus,
        order_status_changed_at: dt.datetime,
        comment: t.Optional[str],
        platform: t.Optional[Membership],
        promo_code: t.Optional[str] = None
    ):
        self.platform = platform
        self.payment_id = payment_id
        self.order_id = order_id
        self.client_id = client_id
        self.order_status_changed_at = order_status_changed_at
        self.order_status = order_status
        self.created_at = created_at
        self.total_price = total_price
        self.id = _id
        self.comment = comment
        self.promo_code = promo_code

    @classmethod
    def create(
        cls,
        order_id: str,
        client_id: int,
        payment_id: str,
        comment: t.Optional[str],
        platform: Membership,
        total_price: Decimal = 0,
        promo_code: t.Optional[str] = None
    ):
        return cls(
            order_id=order_id,
            total_price=total_price,
            client_id=client_id,
            _id=generate_id(),
            payment_id=payment_id,
            created_at=dt.datetime.utcnow(),
            order_status=ClientOrderStatus.AWAIT_PAYMENT,
            order_status_changed_at=dt.datetime.utcnow(),
            comment=comment,
            platform=platform,
            promo_code=promo_code
        )

    def set_objectives(self, objectives: t.List[ClientOrderObjective]):
        map(self.add_client_order_objective, objectives)

    def add_client_order_objective(self, objective: ClientOrderObjective):
        self.total_price += objective.price
        self.objectives.append(objective)

    def __str__(self):
        return f"Order: {self.id} status: {self.order_status}"