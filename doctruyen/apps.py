from django.apps import AppConfig


class DoctruyenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'doctruyen'
    
    def ready(self):
        import doctruyen.signals
