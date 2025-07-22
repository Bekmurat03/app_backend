# payments/models.py
from django.db import models
from django.conf import settings

class SavedUserCard(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_cards')
    card_token = models.CharField(max_length=255, unique=True, verbose_name="Токен карты PayLink")
    card_mask = models.CharField(max_length=20, verbose_name="Маска карты (e.g., 5100...1234)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Карта {self.card_mask} пользователя {self.user.phone}"

    class Meta:
        verbose_name = "Сохраненная карта"
        verbose_name_plural = "Сохраненные карты"