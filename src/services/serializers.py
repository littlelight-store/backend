from rest_framework import serializers

from reviews.models import Review
from reviews.serializers import ProductReviewsSerializer
from .models import Category, PromoCode, PvpThreshold, Season, Service, ServiceConfig, ServiceConfigPvp


class PvpThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = PvpThreshold
        fields = "__all__"


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = "__all__"


class ServiceConfigSerializer(serializers.ModelSerializer):
    threshold_configs = PvpThresholdSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceConfig
        fields = '__all__'


class PvpConfigSerializer(serializers.ModelSerializer):
    threshold_configs = PvpThresholdSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceConfigPvp
        fields = "__all__"


class ExtraCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['slug', 'name']


class ServiceListReviewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ('rate',)


class ServiceListCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('slug', 'name')


class SingleCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class RelatedServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            'slug',
            'title',
            'extra_configs',
            'card_image'
        ]


class ServicesSerializer(serializers.ModelSerializer):
    category = ServiceListCategorySerializer()
    reviews = ServiceListReviewsSerializer(many=True)
    seasons = SeasonSerializer(many=True, read_only=True)
    extra_categories = ExtraCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = (
            'slug', 'category', 'reviews', 'seasons', 'extra_categories', 'title', 'ordering', 'is_new', 'is_hot',
            'extra_configs', 'item_image', 'keywords'
        )


class ServiceSerializer(serializers.ModelSerializer):
    configs = ServiceConfigSerializer(many=True, read_only=True)
    category = SingleCategorySerializer()
    reviews = ProductReviewsSerializer(many=True, read_only=True)
    extra_categories = ExtraCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = "__all__"


class OrderCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class OrderServiceConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceConfig
        fields = '__all__'


class OrderServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['title', 'slug']


class PromoServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['slug']


class PromoCodeSerializer(serializers.ModelSerializer):
    service = PromoServiceSerializer(many=True, read_only=True)

    class Meta:
        model = PromoCode
        fields = "__all__"

