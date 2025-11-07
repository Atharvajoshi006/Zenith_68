from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'Adhyeta Core'

    # Optional: run startup logic or import signals automatically
    # def ready(self):
    #     from . import signals
