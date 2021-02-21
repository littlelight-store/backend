from django.db import models

from profiles.constants import CharacterClasses, Membership


class ORMDestinyBungieProfile(models.Model):
    class Meta:
        db_table = "destiny_bungie_profile"

    membership_id = models.CharField(max_length=500, primary_key=True)
    membership_type = models.IntegerField(choices=(
        (
            Membership.BattleNET.value, Membership.BattleNET,
        ),
        (
            Membership.PS4.value, Membership.PS4,
        ),
        (
            Membership.Steam.value, Membership.Steam,
        ),
        (
            Membership.Xbox.value, Membership.BattleNET,
        )

    ))
    username = models.CharField(max_length=100, null=True, blank=True)
    client_id = models.OneToOneField(
        'profiles.User', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='destiny_profile',
    )

    @property
    def membership(self) -> Membership:
        return Membership(self.membership_type)

    def __str__(self):
        return f"{self.username} -- {self.membership.name}"


class ORMDestinyBungieCharacter(models.Model):
    class Meta:
        db_table = "destiny_bungie_character"

    bungie_profile = models.ForeignKey(
        ORMDestinyBungieProfile,
        on_delete=models.CASCADE,
        related_name='destiny_character',
    )

    character_id = models.CharField(max_length=256, primary_key=True)
    character_class = models.IntegerField(choices=(
        (CharacterClasses.warlock.value, CharacterClasses.warlock),
        (CharacterClasses.titan.value, CharacterClasses.titan),
        (CharacterClasses.hunter.value, CharacterClasses.hunter),
    ))

    @property
    def game_class(self):
        return CharacterClasses(self.character_class)

