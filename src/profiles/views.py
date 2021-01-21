import json

from django.contrib.auth import logout
from django.shortcuts import redirect
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from orders.models import ParentOrder
from .models import BoosterUser, BungieID, EmailSubscription, ProfileCredentials, User
from .serializers import EmailSubscriptionSerializer, UserProfileSerializer


class UserProfileView(RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = User
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class EmailSubscriptionView(CreateAPIView):
    queryset = EmailSubscription
    serializer_class = EmailSubscriptionSerializer


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def create_booster_profile(request: Request):
    data = request.POST

    user_email = data.get('email')

    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        random_password = User.objects.make_random_password()
        user = User.objects.create_user(
            email=user_email, username=user_email, password=random_password
        )

    bungie_profile_data = json.loads(data.get('bungieProfile'))

    bungie_profile, created = BungieID.objects.get_or_create(
        owner=user,
        membership_id=bungie_profile_data["membershipId"],
        membership_type=bungie_profile_data["membershipType"],
        defaults=dict(
            username=bungie_profile_data.get("displayName"),
        ),
    )

    avatar = request.FILES.get('avatar')

    platforms = data.getlist('platforms[]')

    booster = BoosterUser(
        in_game_profile=bungie_profile,
        avatar=avatar,
    )

    booster.save()

    for platform in platforms:
        booster.platforms.add(platform)

    directions = data.getlist('directions[]')

    for direction in directions:
        booster.directions.add(direction)

    user.booster_profile = booster
    user.username = bungie_profile.username
    user.save()

    return Response(True, status=201)


def logout_view(request):
    logout(request)
    response = redirect('/')
    return response


class ProfileCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileCredentials
        fields = ('account_name', 'account_password', 'platform', 'owner')

    def create(self, validated_data):
        return ProfileCredentials.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.account_name = validated_data.get('account_name', instance.account_name)
        instance.account_password = validated_data.get('account_password', instance.account_password)
        instance.save()
        return instance


@api_view(['POST'])
def set_credentials(request: Request):
    data = request.data

    data = {
        **data,
        'owner': request.user.pk
    }

    try:
        credentials = ProfileCredentials.objects.get(owner=request.user, platform=data['platform'])
    except ProfileCredentials.DoesNotExist:
        credentials = None

    if not credentials:
        serializer = ProfileCredentialsSerializer(data=data)
    else:
        serializer = ProfileCredentialsSerializer(credentials, data=data)

    if serializer.is_valid():
        obj: ProfileCredentials = serializer.save()

        ParentOrder.objects.filter(
            orders__bungie_profile__owner=obj.owner,
            credentials=None,
            platform=obj.platform
        ).update(
            credentials=obj
        )

        return Response('ok', status=200)
    else:
        return Response(serializer.errors, status=400)
