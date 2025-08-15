from django.apps import AppConfig


class FilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.files'
    
    def ready(self):
        # Import signals to ensure they are registered
        import apps.files.models