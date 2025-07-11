from django.db import models
from django.conf import settings
from django.db.models import Q
import uuid

class TokenizationAttempt(models.Model):
    """Модель для отслеживания попыток токенизации."""
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('successful', 'Успешно'),
        ('failed', 'Неудачно'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paylink_checkout_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    
    def __str__(self):
        return f"Попытка {self.id} для {self.user.phone}"


class PaymentCard(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_cards')
    name = models.CharField(max_length=50, verbose_name="Название карты", default="Моя карта")
    card_type = models.CharField(max_length=50, default='Visa')
    last_four = models.CharField(max_length=4, verbose_name="Последние 4 цифры")
    expiry_month = models.CharField(max_length=2, verbose_name="Месяц окончания")
    expiry_year = models.CharField(max_length=4, verbose_name="Год окончания")
    card_token = models.CharField(max_length=255, unique=True, verbose_name="Токен карты")
    is_primary = models.BooleanField(default=False, verbose_name="Основная карта")

    class Meta:
        verbose_name = "Платежная карта"
        verbose_name_plural = "Платежные карты"
        ordering = ['-is_primary', '-id']
        constraints = [
            models.UniqueConstraint(fields=['user'], condition=Q(is_primary=True), name='unique_primary_card_for_user')
        ]

    def set_as_primary(self):
        with transaction.atomic():
            PaymentCard.objects.filter(user=self.user, is_primary=True).update(is_primary=False)
            self.is_primary = True
            self.save(update_fields=['is_primary'])

    def __str__(self):
        return f"{self.name} •••• {self.last_four}"