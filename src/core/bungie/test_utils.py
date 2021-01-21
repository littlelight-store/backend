from core.bungie.entities import DestinyBungieProfile, DestinyCharacter
from profiles.constants import CharacterClasses, Membership
from utils import random_guid


def generate_destiny_bungie_profile(membership_type: Membership = Membership.BattleNET):
    return DestinyBungieProfile(
        membership_id=random_guid(),
        membership_type=membership_type,
        username='CoolDude-test'
    )


def generate_destiny_character(
    destiny_profile: DestinyBungieProfile,
    character_class: CharacterClasses = CharacterClasses.warlock,
):
    return DestinyCharacter(
        character_class=character_class,
        character_id=random_guid(),
        bungie_id=destiny_profile.id
    )
