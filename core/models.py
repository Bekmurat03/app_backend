from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager  # 👈 импорт менеджера
from django.db.models import Q

class User(AbstractUser):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('courier', 'Courier'),
        ('restaurant', 'Restaurant'),
        ('admin', 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    is_approved = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, unique=True)

    username = models.CharField(max_length=150, unique=True, blank=True, null=True)

    # 👇👇👇 НАШИ НОВЫЕ ПОЛЯ 👇👇👇
    is_push_enabled = models.BooleanField(default=True, verbose_name="Push-уведомления включены")
    promotions_enabled = models.BooleanField(default=True, verbose_name="Рекламные уведомления")
    # 👆👆👆 КОНЕЦ НОВЫХ ПОЛЕЙ 👆👆👆
    latitude = models.FloatField(null=True, blank=True, verbose_name="Широта курьера")
    longitude = models.FloatField(null=True, blank=True, verbose_name="Долгота курьера")
    
    USERNAME_FIELD = 'phone'       # 👈 логинимся по телефону
    REQUIRED_FIELDS = []           # 👈 другие поля не обязательны

    objects = CustomUserManager()  # 👈 подключаем свой менеджер

    def __str__(self):
        return f"{self.phone} ({self.role})"
class Address(models.Model):
    """
    Модель для хранения адресов пользователей.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='Пользователь')
    title = models.CharField(max_length=100, verbose_name='Название (напр. Дом, Работа)')
    full_address = models.CharField(max_length=255, verbose_name='Полный адрес')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Широта')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name='Долгота')
    is_primary = models.BooleanField(default=False, verbose_name='Основной адрес')

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'
        # У одного пользователя может быть только один основной адрес
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=Q(is_primary=True),
                name='unique_primary_address_for_user'
            )
        ]

    def __str__(self):
        return f'{self.title}: {self.full_address}'