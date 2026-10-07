from django.apps import AppConfig


class SpiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'spi'

    def ready(self):
        from . import stock_signals  # Registra o estorno também nas exclusões em lote.
