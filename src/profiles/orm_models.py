from django.db import models

from core.clients.domain.client import NotificationTokenPurpose, NotificationTokenType
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
    client_id = models.ForeignKey(
        'profiles.User', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='destiny_profiles',
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


class ORMNotificationsPurposes(models.Model):
    value = models.CharField(max_length=52, primary_key=True)
    repr = models.CharField(max_length=52)


class ORMNotificationsToken(models.Model):
    class SourceChoices(models.TextChoices):
        firebase = NotificationTokenType.firebase.value

    client = models.ForeignKey(
        'profiles.User',
        on_delete=models.CASCADE,
        related_name='tokens'
    )
    token = models.CharField(max_length=256)
    source = models.CharField(max_length=32, choices=SourceChoices.choices)
    purposes = models.ManyToManyField(ORMNotificationsPurposes)
    issued_at = models.DateTimeField()
    touched_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(default=None, null=True)

