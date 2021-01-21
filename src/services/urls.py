from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = 'services'
urlpatterns = [
    path('services', views.ServicesListView.as_view(), name='services'),
    path('services/related', views.ServicesRelatedListView.as_view(), name='services'),
    path('service/<slug:slug>', views.ServiceView.as_view(), name='service_view'),
    path('check-promo/', csrf_exempt(views.CheckPromoView.as_view()), name='check-promo'),
]
