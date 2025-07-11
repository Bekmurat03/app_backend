# promos/models.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
from django.db import models, transaction
from django.utils import timezone
from django.db.models import F # 👈 1. Импортируем F-выражения

class PromoBanner(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='promos/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, help_text="Например: 10.0 = 10%")
    expires_at = models.DateTimeField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text="Максимальное количество использований")
    used_count = models.PositiveIntegerField(default=0)

    def is_valid(self):
        """Проверяет, можно ли использовать промокод."""
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False
        return True

    def apply(self):
        """
        Атомарно увеличивает счетчик использования промокода.
        Безопасно для использования в конкурентной среде.
        """
        # 2. 👇 ИСПОЛЬЗУЕМ F() ДЛЯ АТОМАРНОГО ОБНОВЛЕНИЯ
        # Это гарантирует, что даже при одновременных запросах
        # счетчик обновится корректно на уровне базы данных.
        self.used_count = F('used_count') + 1
        self.save(update_fields=['used_count'])
        self.refresh_from_db() # Обновляем объект из БД

    def __str__(self):
        return self.code