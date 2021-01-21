from profiles.constants import CharacterClasses, Membership


class DestinyBungieProfile:
    def __init__(
        self,
        membership_id: str,
        membership_type: Membership,
        username: str
    ):
        self.username = username
        self.membership_type = membership_type
        self.membership_id = membership_id

    @property
    def id(self):
        return self.membership_id


class DestinyCharacter:
    def __init__(
        self,
        character_id: str,
        character_class: CharacterClasses,
        bungie_id: str
    ):
        self.bungie_id = bungie_id
        self.character_class = character_class
        self.character_id = character_id

    @property
    def id(self):
        return self.character_id
