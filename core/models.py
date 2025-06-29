from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager  # 👈 импорт менеджера

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
    notifications_enabled = models.BooleanField(default=True, verbose_name="Основные уведомления")
    promotions_enabled = models.BooleanField(default=True, verbose_name="Рекламные уведомления")
    # 👆👆👆 КОНЕЦ НОВЫХ ПОЛЕЙ 👆👆👆

    USERNAME_FIELD = 'phone'       # 👈 логинимся по телефону
    REQUIRED_FIELDS = []           # 👈 другие поля не обязательны

    objects = CustomUserManager()  # 👈 подключаем свой менеджер

    def __str__(self):
        return f"{self.phone} ({self.role})"
