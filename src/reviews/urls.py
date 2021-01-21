from django.urls import path

from . import views

app_name = 'reviews'
urlpatterns = [
    path('review/<int:order_id>/', views.CreateReviewByOrder.as_view()),
    path('reviews/<slug:service_slug>/', views.ReviewsByServiceListView.as_view(), name='reviews'),
    path('new/reviews/<slug:service_slug>/', views.NewReviewsByServiceListView.as_view(), name='new-reviews'),
]
