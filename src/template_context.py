from django.conf import settings


def base_url():
    return {'base_url': settings.BASE_AUTH_URL}
