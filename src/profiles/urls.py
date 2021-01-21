from django.urls import path

from .views import EmailSubscriptionView, UserProfileView, create_booster_profile, logout_view, set_credentials

app_name = 'profiles'

urlpatterns = [
    path('email-subscription/', EmailSubscriptionView.as_view()),
    path('user/', UserProfileView.as_view()),
    path('user/set-credentials', set_credentials),
    path('booster/sign-in', create_booster_profile),
    path('logout/', logout_view)
]

