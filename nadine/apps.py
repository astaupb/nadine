from django.apps import AppConfig


class NadineConfig(AppConfig):
    name = 'nadine'

    def ready(self):
        # Load and connect signal recievers
        import nadine.signals
