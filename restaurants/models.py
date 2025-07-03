from django.db import models
from django.contrib.auth import get_user_model
from menu.models import MenuCategory

User = get_user_model()

class Restaurant(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="restaurants"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='banners/', blank=True, null=True)  # 🔥 баннер
    address = models.CharField(max_length=255)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    categories = models.ManyToManyField(
        'menu.MenuCategory',  # 👈 ССЫЛКА-СТРОКА
        related_name="restaurants",
        blank=True
    )
    # 👇👇👇 ДОБАВЬТЕ ЭТИ ДВА ПОЛЯ 👇👇👇
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер телефона")
    is_active = models.BooleanField(default=False, verbose_name="Активен (принимает заказы)")
    # 👆👆👆 КОНЕЦ НОВЫХ ПОЛЕЙ 👆👆👆

    # 👇👇👇 ДОБАВЬТЕ ЭТИ ДВА ПОЛЯ 👇👇👇
    latitude = models.FloatField(null=True, blank=True, verbose_name="Широта")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Долгота")
    # 👆👆👆 КОНЕЦ НОВЫХ ПОЛЕЙ 👆👆👆

    def __str__(self):
        return self.name
# 👇👇👇 СОЗДАЕМ НОВУЮ МОДЕЛЬ ДЛЯ ТАРИФОВ 👇👇👇
class DeliveryTariff(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tariffs')
    name = models.CharField(max_length=100, verbose_name="Название тарифа (например, 'Дневной')")
    start_time = models.TimeField(verbose_name="Время начала действия")
    end_time = models.TimeField(verbose_name="Время окончания действия")
    base_fee = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Базовая стоимость (тг)")
    fee_per_km = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Стоимость за км (тг)")

    def __str__(self):
        return f"{self.restaurant.name} - {self.name} ({self.start_time} - {self.end_time})"

    class Meta:
        verbose_name = "Тариф на доставку"
        verbose_name_plural = "Тарифы на доставку"
        ordering = ['start_time']