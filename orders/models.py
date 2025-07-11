import uuid
from django.db import models
from django.conf import settings


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('accepted', 'Принят'),
        ('preparing', 'Готовится'),
        ('ready_for_pickup', 'Готов к выдаче'),
        ('on_the_way', 'В пути'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    PAYMENT_METHOD_CHOICES = [('card_online', 'Картой онлайн'), ('cash', 'Наличными')]

    code = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='orders')
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.SET_NULL, null=True,
                                   related_name='orders')
    courier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='deliveries')
    address = models.TextField()
    delivery_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    comment = models.TextField(blank=True, default='')

    # --- ФИНАНСОВЫЕ ПОЛЯ ---
    items_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Сумма по товарам")
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Стоимость доставки")
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Сервисный сбор")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                      verbose_name="Итоговая сумма к оплате")

    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Прибыль платформы")
    restaurant_payout = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                            verbose_name="Выплата ресторану")
    courier_payout = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Выплата курьеру")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='card_online')
    is_paid = models.BooleanField(default=False)

    # 👇 НОВЫЕ ПОЛЯ для Robokassa
    payment_invoice_id = models.IntegerField(null=True, blank=True, verbose_name="ID счета в Robokassa")
    authorization_id = models.CharField(max_length=255, blank=True, null=True,
                                        verbose_name="ID авторизации (холдирования)")

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"JET-{str(uuid.uuid4()).split('-')[-1].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заказ {self.code}"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu = models.ForeignKey('menu.Dish', on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time_of_order = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.menu.name if self.menu else 'Удаленное блюдо'}"