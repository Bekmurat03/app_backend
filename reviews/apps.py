# reviews/apps.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
from django.apps import AppConfig

class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'

    def ready(self):
        # Импортируем и подключаем сигналы при старте приложения
        import reviews.signals