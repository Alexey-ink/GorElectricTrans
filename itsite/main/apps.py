from django.apps import AppConfig

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
    def ready(self):
        from .models import initialize_vacation_slots  # Импортируйте функцию
        initialize_vacation_slots()  # Вызов функции при запуске приложения


