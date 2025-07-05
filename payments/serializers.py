# apps/payments/serializers.py
from rest_framework import serializers
from .models import PaymentCard

class PaymentCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentCard
        fields = (
            'id',
            'name',  # 👈 добавлено название карты
            'card_type',
            'last_four',
            'expiry_month',
            'expiry_year',
            'is_primary',
        )


class CreatePaymentCardSerializer(serializers.Serializer):
    """
    Сериализатор для ПРИЕМА данных от приложения при добавлении новой карты.
    """
    name = serializers.CharField(required=False, max_length=50)  # 👈 добавлено название карты
    card_number = serializers.CharField(write_only=True, min_length=16, max_length=16)
    expiry_month = serializers.CharField(write_only=True, min_length=2, max_length=2)
    expiry_year = serializers.CharField(write_only=True, min_length=4, max_length=4)
