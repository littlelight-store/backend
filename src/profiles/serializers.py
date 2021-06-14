import typing as t

from rest_framework import serializers

from orders.models import ParentOrder
from .models import (
    BoosterUser, BungieID, EmailSubscription, ProfileCredentials, User, UserCharacter,
)
from .constants import CharacterClasses, Membership


class ProfileCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileCredentials
        fields = "__all__"


class BungieProfileSerializer(serializers.ModelSerializer):
    membership_type_text = serializers.SerializerMethodField()

    class Meta:
        model = BungieID
        fields = '__all__'

    @staticmethod
    def get_membership_type_text(obj):
        return Membership(int(obj.membership_type)).name


class UserCharacterSerializer(serializers.ModelSerializer):
    bungie_profile = BungieProfileSerializer(read_only=True)

    character_class = serializers.SerializerMethodField()

    @staticmethod
    def get_character_class(obj):
        return CharacterClasses(int(obj.character_class)).name

    class Meta:
        model = UserCharacter
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'is_active', 'characters')


class UserReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class EmailSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailSubscription
        fields = ('email',)


class BoosterUserProfile(serializers.ModelSerializer):

    class Meta:
        model = BoosterUser
        fields = ('platforms', 'rating', 'balance', 'avatar')


class UserProfileSerializer(serializers.ModelSerializer):
    booster_profile = BoosterUserProfile()

    should_set_credentials_for = serializers.SerializerMethodField(default=[])

    def get_should_set_credentials_for(self, obj: User) -> t.List[str]:
        platforms = set()

        if not obj.is_booster:
            no_credentials_platforms = ParentOrder.objects.distinct('platform__value').select_related('platform').filter(
                orders__bungie_profile__owner=obj, credentials=None
            )

            if no_credentials_platforms:
                for order in no_credentials_platforms:
                    if order.platform:
                        platforms.add(order.platform.value)

        return list(platforms)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'skype', 'discord', 'is_booster', 'booster_profile',
            'should_set_credentials_for', 'cashback'
        )

        read_only_fields = ('email', 'is_booster', 'should_set_credentials_for', 'cashback')
