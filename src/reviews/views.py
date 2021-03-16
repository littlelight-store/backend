from django.http import Http404
from rest_framework.generics import GenericAPIView, ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response

from reviews.serializers import NewProductReviewsSerializer, ProductReviewsSerializer, ReviewCreateModel
from .models import Review


class ReviewsByServiceListView(ListAPIView):
    serializer_class = ProductReviewsSerializer

    def get_queryset(self):
        service_slug = self.kwargs.get('service_slug')

        return (
            Review
            .objects
            .filter(
                services__slug=service_slug,
                is_posted=True
            )
            .order_by('-created_at')
        )


class NewReviewsByServiceListView(ListAPIView):
    serializer_class = NewProductReviewsSerializer

    def get_queryset(self):
        service_slug = self.kwargs.get('service_slug')

        return (
            Review
            .objects
            .filter(
                services__slug=service_slug,
                is_posted=True
            )
            .order_by('-created_at')
        )


class CreateReviewByOrder(GenericAPIView, UpdateModelMixin):
    serializer_class = ReviewCreateModel

    lookup_field = 'order_id'
    lookup_url_kwarg = 'order_id'

    def get(self, request, order_id):
        query = self.get_queryset()
        if query:
            serializer = self.serializer_class(query.first())
            return Response(data=serializer.data)
        else:
            raise Http404

    def get_object(self):
        return self.get_queryset().first()

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_queryset(self):
        order_id = self.kwargs.get('order_id')
        access_token = self.request.GET.get('access_token')

        return (
            Review
            .objects
            .filter(
                order_id=order_id,
                edit_token=access_token,
                is_posted=False
            )
        )
