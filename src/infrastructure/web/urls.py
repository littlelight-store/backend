
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import service_api
from . import cart_api
from .auth_api import DashboardEmailAuthorization, GetAuthTokenCookie, TokenLogoutAPI
from .client_dashboard_api import ClientDashboardAPI, ClientDashboardCredentialsAPI

urlpatterns = [
    path(f'list-main-page', service_api.list_main_page_goods),
    path(f'service/<str:slug>/page/', service_api.get_service_page),
    path('cart/payed', cart_api.cart_payed, name='v2_cart_payed'),
    path('cart/apply-promo', cart_api.apply_promo, name='v2_apply_promo'),
    path('cart/delete', cart_api.cart_delete, name='v2_cart_delete'),
    path('cart/add', cart_api.add_item_to_cart, name='v2_add_to_caft'),
    path('cart/list', cart_api.list_cart_items, name='v2_list_cart_items'),
    path('dashboard', ClientDashboardAPI.as_view()),
    path('dashboard-credentials', ClientDashboardCredentialsAPI.as_view()),
    path('auth/get-auth-token', GetAuthTokenCookie.as_view()),
    path('auth/auth-email-token', DashboardEmailAuthorization.as_view()),
    path('auth/logout', TokenLogoutAPI.as_view())
]
