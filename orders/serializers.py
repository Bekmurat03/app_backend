# orders/serializers.py

from django.db import transaction
from rest_framework import serializers
from .models import Order, OrderItem
from menu.models import Dish
from core.models import Address
from restaurants.serializers import RestaurantSerializer
from menu.serializers import DishSerializer
from .services import calculate_delivery_fee

class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ОДНОГО товара в заказе."""
    menu = DishSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu', 'quantity', 'price_at_time_of_order']


class CreateOrderSerializer(serializers.Serializer):
    """
    Сериализатор для ПРИЕМА данных от клиента и СОЗДАНИЯ заказа со всеми расчетами.
    """
    items = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()), write_only=True, required=True
    )
    address_id = serializers.IntegerField(write_only=True, required=True)
    comment = serializers.CharField(required=False, allow_blank=True, write_only=True)
    promo_code = serializers.CharField(required=False, allow_blank=True, write_only=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Корзина не может быть пустой.")
        
        # Проверяем, что все товары из одного ресторана
        restaurant_id = None
        for item_data in items:
            dish_id = item_data.get('dish_id')
            if not dish_id:
                raise serializers.ValidationError("Каждый товар должен содержать 'dish_id'.")
            
            dish = Dish.objects.filter(id=dish_id).first()
            if not dish:
                raise serializers.ValidationError(f"Блюдо с ID {dish_id} не найдено.")
            
            if restaurant_id is None:
                restaurant_id = dish.restaurant.id
            elif restaurant_id != dish.restaurant.id:
                raise serializers.ValidationError("Все товары в заказе должны быть из одного ресторана.")
        return items

    def create(self, validated_data):
        """
        Этот метод создает заказ и рассчитывает все стоимости, вызывая сервис доставки.
        """
        items_data = validated_data.pop('items')
        address_id = validated_data.pop('address_id')
        promo_code_str = validated_data.pop('promo_code', None)
        user = self.context['request'].user

        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            raise serializers.ValidationError("Указанный адрес не найден или не принадлежит вам.")

        first_dish_id = items_data[0]['dish_id']
        restaurant = Dish.objects.get(id=first_dish_id).restaurant

        with transaction.atomic():
            # Создаем сам заказ
            order = Order.objects.create(
                user=user,
                restaurant=restaurant,
                address_text=f"{address.city}, {address.street}, {address.house_number}",
                delivery_lat=address.latitude,
                delivery_lon=address.longitude,
                **validated_data
            )

            # Создаем позиции заказа и считаем итоговую сумму товаров
            items_total_price = Decimal(0)
            order_items_to_create = []
            for item_data in items_data:
                dish = Dish.objects.get(id=item_data['dish_id'])
                price = dish.price
                quantity = item_data['quantity']
                items_total_price += price * quantity
                order_items_to_create.append(
                    OrderItem(order=order, dish=dish, quantity=quantity, price_at_time_of_order=price)
                )
            
            OrderItem.objects.bulk_create(order_items_to_create)

            # --- ЛОГИКА РАСЧЕТОВ ---
            discount = Decimal(0)
            if promo_code_str:
                try:
                    promo = PromoCode.objects.get(code__iexact=promo_code_str)
                    if promo.is_valid():
                        discount = promo.calculate_discount(items_total_price) 
                        order.promo_code = promo
                except PromoCode.DoesNotExist:
                    pass
            
            # 👇 2. ВЫЗЫВАЕМ СЕРВИС ДЛЯ РЕАЛЬНОГО РАСЧЕТА ДОСТАВКИ
            delivery_fee = calculate_delivery_fee(restaurant, address)
            
            # 👇 3. РАСЧЕТ СЕРВИСНОГО СБОРА (из вашей логики)
            service_fee = max(
                Decimal(settings.MIN_CLIENT_SERVICE_FEE),
                min(
                    items_total_price * (Decimal(settings.CLIENT_SERVICE_FEE_PERCENT) / 100),
                    Decimal(settings.MAX_CLIENT_SERVICE_FEE)
                )
            )

            # 👇 4. РАСЧЕТ ВЫПЛАТ И КОМИССИЙ (из вашей логики)
            platform_commission = items_total_price * (Decimal(settings.RESTAURANT_COMMISSION_PERCENT) / 100)
            
            # Рассчитываем финальную стоимость
            total_price = items_total_price + delivery_fee + service_fee - discount

            # Сохраняем все рассчитанные значения в заказ
            order.items_total_price = items_total_price
            order.delivery_fee = delivery_fee
            order.service_fee = service_fee
            order.discount_amount = discount
            order.total_price = total_price
            order.platform_fee = platform_commission + service_fee
            order.restaurant_payout = items_total_price - platform_commission
            order.courier_payout = delivery_fee
            order.save()

        return order

class OrderSerializer(serializers.ModelSerializer):
    """Полный сериализатор для отображения информации о заказе."""
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant = RestaurantSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        # Убедитесь, что все эти поля есть в вашей модели Order
        fields = [
            'id', 'code', 'address_text', 'comment', 'items_total_price',
            'delivery_fee', 'service_fee', 'discount_amount', 'total_price', 'platform_fee',
            'restaurant_payout', 'courier_payout', 'status', 'created_at',
            'is_paid', 'restaurant', 'items', 'user'
        ]

class OrderDetailSerializer(OrderSerializer):
    """Детальный сериализатор, наследует все от OrderSerializer."""

    class Meta(OrderSerializer.Meta):
        pass