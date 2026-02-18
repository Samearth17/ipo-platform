from django.apps import AppConfig


class IpoConfig(AppConfig):
    name = 'ipo'

    def ready(self):
        import ipo.signals
