# payments/serializers.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
from rest_framework import serializers
from .models import PaymentCard

class PaymentCardSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения данных о сохраненной карте."""
    class Meta:
        model = PaymentCard
        # Добавляем поле name для удобства пользователя
        fields = ('id', 'name', 'card_type', 'last_four', 'is_primary')


class CardCreateSerializer(serializers.Serializer):
    """Сериализатор для ПРИЕМА токена от фронтенда."""
    card_token = serializers.CharField(required=True, write_only=True)
    name = serializers.CharField(required=False, allow_blank=True) # Позволяем пользователю задать имя карте