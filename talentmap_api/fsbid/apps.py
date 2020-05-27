from django.apps import AppConfig


class FsbidConfig(AppConfig):
    name = 'fsbid'

    def ready(self):
        import fsbid.signals
