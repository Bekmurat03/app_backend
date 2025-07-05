from django.db import models
from django.conf import settings

class PaymentCard(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_cards')

    name = models.CharField(  # 👈 Добавляем название карты
        max_length=50,
        verbose_name="Название карты",
        default="Моя карта"
    )

    card_type = models.CharField(max_length=50, default='Visa')
    last_four = models.CharField(max_length=4, verbose_name="Последние 4 цифры")
    expiry_month = models.CharField(max_length=2, verbose_name="Месяц окончания")
    expiry_year = models.CharField(max_length=4, verbose_name="Год окончания")
    card_token = models.CharField(max_length=255, unique=True, verbose_name="Токен карты", null=True)
    is_primary = models.BooleanField(default=False, verbose_name="Основная карта")

    def __str__(self):
        return f"{self.name} •••• {self.last_four}"

    class Meta:
        verbose_name = "Платежная карта"
        verbose_name_plural = "Платежные карты"
