# app_backend/apps/orders/serializers.py (ФИНАЛЬНАЯ ВЕРСИЯ БЕЗ ОШИБКИ ФОРМАТА)

from rest_framework import serializers
from restaurants.serializers import RestaurantSerializer
from .models import Order, OrderItem
from menu.models import Dish
from core.models import Address
from django.utils import timezone
import math
from decimal import Decimal
from django.db.models import F # 👈 1. ИМПОРТИРУЕМ F() EXPRESSION

# --- Вспомогательная функция для расчета расстояния ---
def get_distance(lat1, lon1, lat2, lon2):
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 0
    R = 6371
    rad = lambda x: float(x) * math.pi / 180
    
    dLat = rad(Decimal(lat2) - Decimal(lat1))
    dLon = rad(Decimal(lon2) - Decimal(lon1))
    
    a = (math.sin(dLat / 2) ** 2) + math.cos(rad(Decimal(lat1))) * math.cos(rad(Decimal(lat2))) * (math.sin(dLon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

# --- Сериализатор для ОДНОГО товара в заказе ---
class OrderItemDishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ['id', 'name', 'image', 'price', 'restaurant']


class OrderItemSerializer(serializers.ModelSerializer):
    # menu_item теперь будет содержать объект со всеми нужными данными
    menu_item = OrderItemDishSerializer(source='menu', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu', 'quantity', 'menu_item', 'price_at_time_of_order']
        extra_kwargs = {
            'menu': {'write_only': True}
        }


# --- Основной сериализатор для Заказа ---
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    restaurant = RestaurantSerializer(read_only=True)
    address_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'code', 'address', 'comment', 'total_price',
            'delivery_fee', 'status', 'created_at', 'items', 'restaurant',
            'address_id', 'preparation_time', 'estimated_delivery_time'
        ]
        read_only_fields = (
            'status', 'created_at', 'total_price', 'code',
            'restaurant', 'delivery_fee', 'user', 'address','preparation_time', 'estimated_delivery_time'
        )

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        address_id = validated_data.pop('address_id')
        user = self.context['request'].user

        if not items_data:
            raise serializers.ValidationError("Нельзя создать пустой заказ.")

        try:
            address_obj = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            raise serializers.ValidationError("Указанный адрес не найден.")

        first_dish = items_data[0]['menu']
        restaurant = first_dish.restaurant

        delivery_fee = Decimal('0.00')
        if restaurant.tariffs.exists() and restaurant.latitude and address_obj.latitude:
            distance = get_distance(address_obj.latitude, address_obj.longitude, restaurant.latitude, restaurant.longitude)
            
            now = timezone.now().time()
            active_tariff = None
            
            # 👇 2. ИСПРАВЛЕНО: Используем F('end_time') вместо строки 'end_time'
            night_tariff = restaurant.tariffs.filter(start_time__gt=F('end_time')).first()
            
            if night_tariff and (now >= night_tariff.start_time or now < night_tariff.end_time):
                active_tariff = night_tariff
            else:
                active_tariff = restaurant.tariffs.filter(start_time__lte=now, end_time__gt=now).first()

            if active_tariff:
                calculated_cost = active_tariff.base_fee + (Decimal(distance) * active_tariff.fee_per_km)
                delivery_fee = Decimal(round(calculated_cost / 50) * 50)

        validated_data['address'] = address_obj.full_address
        validated_data['user'] = user
        validated_data['delivery_lat'] = address_obj.latitude
        validated_data['delivery_lon'] = address_obj.longitude

        order = Order.objects.create(
            restaurant=restaurant,
            delivery_fee=delivery_fee,
            **validated_data
        )

        total_items_price = Decimal('0.00')
        for item_data in items_data:
            dish = item_data['menu']
            quantity = item_data['quantity']
            price_at_time_of_order = dish.price
            OrderItem.objects.create(order=order, menu=dish, quantity=quantity, price_at_time_of_order=price_at_time_of_order)
            total_items_price += price_at_time_of_order * quantity

        order.total_price = total_items_price + delivery_fee
        order.save()

        return order