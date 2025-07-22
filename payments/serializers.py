# payments/serializers.py
from rest_framework import serializers
# 👇 ИСПРАВЛЯЕМ ИМПОРТ: используем правильное имя модели
from .models import SavedUserCard 

class SavedUserCardSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения данных о сохраненной карте."""
    class Meta:
        # 👇 ИСПРАВЛЯЕМ МОДЕЛЬ
        model = SavedUserCard
        # Указываем поля, которые есть в нашей модели SavedUserCard
        fields = ('id', 'card_token', 'card_mask')


# Этот сериализатор пока не используется, но мы его оставим на будущее,
# если вы захотите реализовать привязку карты отдельным шагом.
class CardCreateSerializer(serializers.Serializer):
    """Сериализатор для ПРИЕМА токена от фронтенда."""
    card_token = serializers.CharField(required=True, write_only=True)
    name = serializers.CharField(required=False, allow_blank=True)