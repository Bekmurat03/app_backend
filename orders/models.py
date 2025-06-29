from django.db import models
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant
from menu.models import Dish
import random

User = get_user_model()

ORDER_STATUS_CHOICES = [
    ('pending', 'В ожидании'),
    ('accepted', 'Принят'),
    ('preparing', 'Готовится'),
    ('on_the_way', 'В пути'),
    ('delivered', 'Доставлен'),
    ('cancelled', 'Отменён'),
]

def generate_order_code():
    while True:
        code = f"{random.randint(0, 999):03d}-{random.randint(0, 999):03d}"
        if not Order.objects.filter(code=code).exists():
            return code

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="orders", null=True, blank=True)

    code = models.CharField(max_length=10, unique=True, blank=True)  # Код заказа (например: 123-456)
    address = models.CharField(max_length=255)
    comment = models.TextField(blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    courier = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, # Если курьера удалят, заказ не удалится
        related_name="deliveries", 
        null=True, 
        blank=True
    )
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_order_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заказ {self.code or self.id} от {self.user.phone}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.menu.name}"
