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

    def __str__(self):
        return self.name
