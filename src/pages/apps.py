from django.apps import AppConfig


class PagesConfig(AppConfig):
    name = "pages"

    def ready(self):
        from infrastructure.wire import wire_api

        wire_api()
