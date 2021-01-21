from django.urls import path
from django.views.decorators.csrf import csrf_exempt

import infrastructure.web.cart_api
from . import v2_views, views

app_name = 'orders'
urlpatterns = [
    path('invoice/complete', views.invoice_complete),
    path('order/', views.process_create_order, name='order'),
    path('v2/order/', v2_views.create_order, name='v2_order'),
    path('featured/week', views.OrderCompletedLastWeekAPIView.as_view(), name='featured-orders'),
    path('user/orders/', views.UserOrdersView.as_view()),
    path('user/booster/orders/', views.UserBoosterOrdersView.as_view()),
    path('user/order/<int:pk>/', csrf_exempt(views.UserOrderView.as_view())),
    path('order/credentials/<int:order_id>/', views.OrderCredentialsView.as_view()),
    path('user/booster/order/<int:pk>/', csrf_exempt(views.UserBoosterOrderView.as_view()))
]
