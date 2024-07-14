from django.apps import AppConfig


class ResfinalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'resfinal'
    def ready(self):
        import resfinal.signal
