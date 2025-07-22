# orders/models.py

import uuid
from django.db import models
from django.conf import settings
from decimal import Decimal


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

    code = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='orders')
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.SET_NULL, null=True,
                                   related_name='orders')
    courier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='deliveries')
    address_text = models.TextField(verbose_name="Адрес доставки (текст)", default="Без адреса")
    delivery_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    comment = models.TextField(blank=True, default='')

    # --- Финансовые поля ---
    items_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Сумма по товарам")
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Стоимость доставки")
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Сервисный сбор")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                      verbose_name="Итоговая сумма к оплате")

    # --- Поля для расчетов выплат ---
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Прибыль платформы")
    restaurant_payout = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                            verbose_name="Выплата ресторану")
    courier_payout = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Выплата курьеру")

    # --- Статус и оплата ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False, verbose_name="Оплачен")

    # 👇 ПОЛЯ payment_method и authorization_id УДАЛЕНЫ

    # Поле для Robokassa. В него мы записываем ID нашего заказа, чтобы связать платеж.
    payment_invoice_id = models.IntegerField(null=True, blank=True, verbose_name="ID счета в Robokassa")

    def save(self, *args, **kwargs):
        if not self.code:
            # Генерируем уникальный и более короткий код заказа
            self.code = f"JT-{str(uuid.uuid4().int)[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заказ {self.code}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu = models.ForeignKey('menu.Dish', on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time_of_order = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена на момент заказа")

    def __str__(self):
        return f"{self.quantity} x {self.menu.name if self.menu else 'Удаленное блюдо'}"

    class Meta:
        verbose_name = "Позиция в заказе"
        verbose_name_plural = "Позиции в заказе"