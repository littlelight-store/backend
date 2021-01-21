from rest_framework.serializers import ModelSerializer

from profiles.serializers import UserReviewSerializer
from services.models import Service
from .models import Review


class ProductReviewsSerializer(ModelSerializer):
    author = UserReviewSerializer()

    class Meta:
        model = Review
        fields = '__all__'


class NewProductReviewsSerializer(ModelSerializer):

    class Meta:
        model = Review
        fields = ('author_string', 'rate', 'text', 'id', 'last_edited')


class ReviewServiceSerializer(ModelSerializer):
    class Meta:
        model = Service
        fields = ('title', 'slug')


class ReviewCreateModel(ModelSerializer):
    author = UserReviewSerializer(read_only=True)
    services = ReviewServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Review
        exclude = ('edit_token', 'created_at', 'last_edited', 'is_sent_to_user')
        read_only_fields = ('order',)
