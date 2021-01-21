import typing as t
from pydantic import BaseModel

from core.domain.entities.bungie_profile import DestinyCharacterClass
from profiles.constants import CharacterClasses, Membership


class EventOrderCreatedOptionDTO(BaseModel):
    description: str
    price: str


class EventOrderCreatedDTO(BaseModel):
    service_title: str
    total_price: str
    platform: Membership
    character_class: t.Union[DestinyCharacterClass, CharacterClasses]
    promo_code: t.Optional[str]
    options: t.List[EventOrderCreatedOptionDTO]
    user_email: str
    username: str
