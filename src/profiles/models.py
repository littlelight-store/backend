from enum import Enum

from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import CharacterClasses, Membership
from .orm_models import ORMDestinyBungieProfile, ORMDestinyBungieCharacter


class BungiePlatform(models.Model):
    name = models.CharField(max_length=20)
    value = models.IntegerField(primary_key=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    def __str__(self):

        role = 'booster' if self.is_booster else 'client'
        return f"<{role.upper()}> {self.email}"

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    username = models.CharField(
        'username',
        max_length=150,
        unique=False,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
    )

    booster_profile = models.ForeignKey(
        'profiles.BoosterUser',
        on_delete=models.SET_NULL, related_name='user',
        null=True, default=None, blank=True
    )

    is_booster = models.BooleanField(default=False)

    email = models.EmailField('email address', unique=True, db_index=True)

    discord = models.CharField(max_length=100, blank=True, null=True)
    skype = models.CharField(max_length=100, blank=True, null=True)
    cashback = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text='Cashback balance', blank=True
    )
    last_chat_message_send_at = models.DateTimeField(null=True, blank=True)


class BoosterCategories(Enum):
    pvp = 'pvp'
    pve = 'pve'


class Direction(models.Model):
    slug = models.SlugField(primary_key=True)


class BoosterUser(models.Model):
    in_game_profile = models.ForeignKey('profiles.BungieID', on_delete=models.SET_NULL, null=True)
    rating = models.FloatField(default=0, help_text='User rating')

    discord_id = models.CharField(
        max_length=50, help_text='Discord id. Ex: test#1234', default=None, null=True, blank=True
    )

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Balance')
    avatar = models.ImageField(upload_to='boosters', help_text='User avatar', default='')

    total_orders_base = models.IntegerField(
        default=0, help_text='Базовое число к которому сумируются кол-во заказов в сервисе'
    )

    directions = models.ManyToManyField(Direction, blank=True)

    platforms = models.ManyToManyField(
        'BungiePlatform',
        help_text='Booster platforms',
        related_name='boosters'
    )

    def __str__(self):
        return (
            f'profile: {self.in_game_profile}'
            f'rating: {self.rating}, '
        )

    class Meta:
        verbose_name = 'Booster user'
        verbose_name_plural = 'Boosters'


class UserCharacter(models.Model):
    bungie_profile = models.ForeignKey(
        'BungieID',
        on_delete=models.CASCADE,
        related_name='characters',
        blank=True, null=True
    )

    character_id = models.CharField(max_length=500)
    character_class = models.CharField(
        max_length=10,
    )

    @classmethod
    def get_class_repr(cls, class_value_or_name):
        if type(class_value_or_name) == str:
            found_class = CharacterClasses(class_value_or_name)

            if found_class:
                return found_class.name
        else:
            return None

    def __str__(self):
        return f"{self.character_id} -- {self.character_class}"


class BungieID(models.Model):
    owner = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='bungie_profiles'
    )

    id = models.AutoField(primary_key=True)

    membership_id = models.CharField(max_length=500)
    membership_type = models.CharField(max_length=20)
    username = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"[{self.membership_id}] {self.owner.email} -- {Membership(int(self.membership_type)).name}"


class ProfileCredentials(models.Model):
    account_name = models.CharField(max_length=120)
    account_password = models.CharField(max_length=120)

    platform = models.ForeignKey(
        'profiles.BungiePlatform', on_delete=models.CASCADE, null=True
    )

    owner = models.ForeignKey(
        'profiles.User',
        on_delete=models.CASCADE,
        related_name='credentials',
        blank=True, null=True
    )

    is_expired = models.BooleanField(
        default=False
    )

    @classmethod
    def create_or_update_platform_credentials(cls, user, platform, account_name, account_password):
        instance, _ = cls.objects.update_or_create(
            owner=user, platform=platform,
            defaults=dict(
                account_name=account_name,
                account_password=account_password
            )
        )

        return instance

    def __str__(self):
        return f'{self.owner} -> {self.platform}'

    class Meta:
        unique_together = [['platform', 'owner']]


class EmailSubscription(models.Model):
    email = models.EmailField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
