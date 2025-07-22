from django.db import models
from django.conf import settings


class Restaurant(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='restaurants')
    name = models.CharField(max_length=255)
    description = models.TextField()
    logo = models.ImageField(upload_to='restaurant_logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='restaurant_banners/', blank=True, null=True)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=20, blank=True)
    categories = models.ManyToManyField('menu.MenuCategory', related_name='restaurants')

    # 👇 НОВОЕ ПОЛЕ: ID дополнительного магазина этого ресторана в Robokassa
    robokassa_login = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Логин ресторана в Robokassa"
    )

    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name="Средний рейтинг")
    review_count = models.PositiveIntegerField(default=0, verbose_name="Количество отзывов")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.name


class DeliveryTariff(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tariffs')
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    base_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Базовая стоимость")
    fee_per_km = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость за км")

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"