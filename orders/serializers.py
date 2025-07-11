# orders/serializers.py (ПОЛНЫЙ КОД С ИСПРАВЛЕНИЕМ)

from rest_framework import serializers
from .models import Order, OrderItem
from menu.serializers import DishSerializer
from restaurants.serializers import RestaurantSerializer
# 👇 ИМПОРТ UserSerializer УДАЛЕН, чтобы разорвать цикл

class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ОДНОГО товара в заказе."""
    menu = DishSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'menu', 'quantity', 'price_at_time_of_order']

class OrderCreateSerializer(serializers.Serializer):
    """Сериализатор для ПРИЕМА данных от клиента при создании заказа."""
    items = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )
    address_id = serializers.IntegerField(write_only=True)
    card_id = serializers.IntegerField(write_only=True, required=False)
    comment = serializers.CharField(required=False, allow_blank=True, write_only=True)

class OrderSerializer(serializers.ModelSerializer):
    """Полный сериализатор для отображения информации о заказе."""
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant = RestaurantSerializer(read_only=True)
    
    # 👇 ГЛАВНОЕ ИЗМЕНЕНИЕ: Вместо вложенного UserSerializer используем StringRelatedField.
    # Он просто вызовет метод __str__ у модели User (который у нас возвращает номер телефона).
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'code', 'address', 'comment', 'items_total_price',
            'delivery_fee', 'service_fee', 'total_price', 'platform_fee',
            'restaurant_payout', 'courier_payout', 'status', 'created_at',
            'is_paid', 'payment_id', 'authorization_id', 'restaurant', 'items',
            'user'
        ]