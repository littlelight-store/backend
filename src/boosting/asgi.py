"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boosting.settings')
django_asgi_app = get_asgi_application()

from infrastructure.ws.chat.auth import TokenAuthMiddleware
from infrastructure.ws.chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": TokenAuthMiddleware(
        URLRouter(
            chat_websocket_urlpatterns
        )
    ),
})
