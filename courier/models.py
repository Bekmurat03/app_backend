# courier/models.py
from django.db import models
from django.conf import settings

class CourierProfile(models.Model):
    VERIFICATION_STATUS_CHOICES = [
        ('not_submitted', 'Не подано'),
        ('on_review', 'На проверке'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courier_profile'
    )
    
    # Поля для документов
    id_card_photo = models.ImageField(upload_to='courier_documents/', verbose_name="Фото удостоверения")
    driver_license_photo = models.ImageField(upload_to='courier_documents/', blank=True, null=True, verbose_name="Фото водит. прав")
    
    # Статус верификации, который будет менять администратор
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='not_submitted',
        verbose_name="Статус верификации"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_online = models.BooleanField(default=False, verbose_name="На линии")
    
    def __str__(self):
        return f"Профиль курьера: {self.user.get_full_name() or self.user.phone}"

    class Meta:
        verbose_name = "Профиль курьера"
        verbose_name_plural = "Профили курьеров"