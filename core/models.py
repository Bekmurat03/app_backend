from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models

from jetfood_backend import settings
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    
    # 👇 ДОБАВЛЯЕМ НЕДОСТАЮЩИЕ ПОЛЯ
    city = models.CharField(max_length=100, verbose_name="Город", default='Unknown')
    street = models.CharField(max_length=255, verbose_name="Улица",default='Unknown')
    house_number = models.CharField(max_length=20, verbose_name="Номер дома", default='Unknown')
    
    # Поля для координат
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Можете добавить и другие поля, если нужно
    # entrance = models.CharField(max_length=10, blank=True, verbose_name="Подъезд")
    # floor = models.CharField(max_length=10, blank=True, verbose_name="Этаж")
    # apartment = models.CharField(max_length=10, blank=True, verbose_name="Квартира")

    is_primary = models.BooleanField(default=False, verbose_name="Основной адрес")

    def __str__(self):
        return f"{self.city}, {self.street}, {self.house_number}"

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"
class PhoneOTP(models.Model):
    """
    Модель для хранения временных OTP кодов для верификации номера телефона.
    """
    phone = models.CharField(max_length=20, unique=True, verbose_name="Номер телефона")
    otp = models.CharField(max_length=4, verbose_name="OTP код")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    def is_expired(self):
        """
        Проверяет, не истек ли срок действия OTP (например, 5 минут).
        """
        return self.created_at < timezone.now() - timedelta(minutes=5)

    def __str__(self):
        return f"OTP {self.otp} для номера {self.phone}"

    class Meta:
        verbose_name = "OTP код"
        verbose_name_plural = "OTP коды"