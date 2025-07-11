# promos/serializers.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
from rest_framework import serializers
from .models import PromoBanner, PromoCode

class PromoBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoBanner
        fields = ['id', 'title', 'description', 'image', 'is_active', 'created_at']


class PromoCodeSerializer(serializers.ModelSerializer):
    # Добавляем поле "только для чтения", чтобы показать, валиден ли код
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = PromoCode
        fields = ['id', 'code', 'discount', 'is_valid'] # Отдаем только нужную информацию