from rest_framework import serializers
from restaurants.serializers import RestaurantSerializer
from .models import Order, OrderItem
from menu.models import Dish

class OrderItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='menu.name', read_only=True)
    image = serializers.ImageField(source='menu.image', read_only=True)
    price = serializers.DecimalField(source='menu.price', max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu', 'name', 'image', 'price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    total_price = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    code = serializers.CharField(read_only=True)
    restaurant = RestaurantSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'code',
            'address',
            'comment',
            'total_price',
            'status',
            'created_at',
            'items',
            'restaurant',
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        validated_data.pop('user', None)
        user = self.context['request'].user

        # Получаем ресторан из первого блюда
        first_menu_item = items_data[0]['menu']
        restaurant = first_menu_item.restaurant

        # Создаём заказ с рестораном
        order = Order.objects.create(user=user, restaurant=restaurant, **validated_data)

        total = 0
        for item_data in items_data:
            menu = item_data['menu']
            quantity = item_data['quantity']
            price = menu.price * quantity
            OrderItem.objects.create(order=order, menu=menu, quantity=quantity)
            total += price

        order.total_price = total
        order.save()
        # 👇👇👇 ВОТ НАША ЗАГЛУШКА 👇👇👇
        # TODO: В будущем здесь будет логика отправки пуш-уведомления
        # в приложение ресторана о том, что поступил новый заказ.
        # send_push_notification(restaurant.owner.device_token, f"Новый заказ #{order.code}")
        # 👆👆👆 КОНЕЦ ЗАГЛУШКИ 👆👆👆
        return order
