from rest_framework import serializers

from profiles.models import BoosterUser, BungieID, ProfileCredentials, User, UserCharacter
from services.models import Service
from services.serializers import OrderServiceSerializer
from .models import Order, PvpConfigOrder


class PvpConfigOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PvpConfigOrder
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    service = OrderServiceSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('created_at', 'service', 'id', 'is_order_complete', 'status')
        write_only = ('data_completed', 'booster_telegram_id')


class OrderBungieProfile(serializers.ModelSerializer):
    class Meta:
        model = BungieID
        fields = ('id', 'membership_id', 'membership_type', 'username')


class OrderBungieCharacter(serializers.ModelSerializer):
    class Meta:
        model = UserCharacter
        fields = ('character_id', 'character_class')


class UserOrderServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            'slug',
            'title',
            'option_type',
            'image_square'
        )


class BungieProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BungieID

        fields = (
            "username",
        )


class OrderBoosterProfileSerializer(serializers.ModelSerializer):
    in_game_profile = BungieProfileSerializer()
    total_orders = serializers.SerializerMethodField()

    @staticmethod
    def get_total_orders(instance):
        return instance.total_orders_base

    class Meta:
        model = BoosterUser
        fields = (
            'rating',
            'avatar',
            'total_orders',
            'in_game_profile'
        )


class OrderBoosterUserSerializer(serializers.ModelSerializer):
    booster_profile = OrderBoosterProfileSerializer()

    class Meta:
        model = User
        fields = (
            "username",
            "booster_profile",
        )


class BoosterOrdersSerializer(serializers.ModelSerializer):
    service = UserOrderServiceSerializer()

    bungie_profile = OrderBungieProfile()
    character = OrderBungieCharacter()

    booster_user = OrderBoosterUserSerializer()

    class Meta:
        model = Order
        fields = (
            'total_price',
            'service',
            'status',
            'id',
            'taken_at',
            'complete_at',
            'created_at',
            'total_price',
            'layout_options',
            'bungie_profile',
            'booster_price',
            'character',
            'booster_user'
        )


class UserOrderSerializer(serializers.ModelSerializer):
    service = UserOrderServiceSerializer()

    bungie_profile = OrderBungieProfile()
    character = OrderBungieCharacter()

    booster_user = OrderBoosterUserSerializer()

    class Meta:
        model = Order
        fields = (
            'total_price',
            'service',
            'status',
            'id',
            'taken_at',
            'complete_at',
            'created_at',
            'total_price',
            'layout_options',
            'bungie_profile',
            'character',
            'booster_user'
        )


class OrderCredentialsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ('status', 'complete_at')


class UserOrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status', 'complete_at')

    def update(self, instance, validated_data):
        return super(UserOrderUpdateSerializer, self).update(instance, validated_data)


class ProfileCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileCredentials
        fields = ('account_name', 'account_password', 'platform')


class UserBoosterOrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status', 'complete_at')

    def update(self, instance, validated_data):
        return super(UserBoosterOrderUpdateSerializer, self).update(instance, validated_data)
