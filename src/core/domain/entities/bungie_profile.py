import enum
import typing as t

from pydantic import BaseModel, Field

from ..object_values import MembershipId
from core.domain.entities.interfaces import IBooster, IClient
from profiles.constants import Membership


class DestinyCharacterClass(int, enum.Enum):
    titan = 0
    hunter = 1
    warlock = 2


class BungieProfileDTO(BaseModel):
    membership_id: MembershipId = Field(..., alias='membershipId')
    membership_type: Membership = Field(..., alias='membershipType')
    username: str = Field(..., alias='displayName')


class BungieProfile:
    membership_type: Membership
    characters: t.Dict[str, 'DestinyCharacter']

    def __init__(
        self,
        membership_id: MembershipId,
        membership_type: str,
        username: str,
        owner: t.Union[IClient, IBooster],
        owner_id: int,
        _id: int,
        characters: t.List['DestinyCharacter'] = None
    ):
        if not characters:
            characters = []

        self.membership_id = membership_id
        self.membership_type = Membership(int(membership_type))
        self.username = username
        self.owner = owner
        self.owner_id = owner_id
        self.id = _id
        self.characters = self._map_characters(characters)

    @staticmethod
    def _map_characters(characters: t.List['DestinyCharacter']):
        result = dict()
        for character in characters:
            result[character.character_id] = character
        return result

    def set_characters(self, characters: t.List['DestinyCharacter']):
        self.characters = self._map_characters(characters)

    def get_character(self, character_id: str) -> 'DestinyCharacter':
        return self.characters[character_id]


class DestinyCharacter(BaseModel):
    id: t.Optional[int] = Field(None)
    character_id: str = Field(..., alias='characterId')
    character_class: DestinyCharacterClass = Field(..., alias='classType')
