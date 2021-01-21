from django.apps import AppConfig


class PagesConfig(AppConfig):
    name = "pages"

    def ready(self):
        from boosting import container
        from infrastructure.web.wire_api import wire_api

        wire_api()
