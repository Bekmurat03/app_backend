# reviews/serializers.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
from rest_framework import serializers
from .models import Review
from orders.models import Order
from core.serializers import UserSerializer # Используем готовый сериализатор пользователя

class PublicReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для публичного отображения отзывов (например, на странице ресторана)."""
    user = UserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'user', 'rating', 'comment', 'created_at')


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и управления своими отзывами."""
    class Meta:
        model = Review
        fields = ('id', 'order', 'rating', 'comment', 'created_at')
        read_only_fields = ('user', 'created_at') # Пользователь подставится автоматически

    def validate_order(self, order):
        """Проверяем, что пользователь может оставить отзыв на этот заказ."""
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Ошибка контекста запроса.")

        # 1. Проверяем, что заказ принадлежит пользователю
        if order.user != request.user:
            raise serializers.ValidationError("Вы не можете оставить отзыв на чужой заказ.")
            
        # 2. Проверяем, что заказ доставлен
        if order.status != 'delivered':
            raise serializers.ValidationError("Вы можете оставить отзыв только на доставленный заказ.")
            
        # 3. Проверяем, что на этот заказ еще нет отзыва
        if Review.objects.filter(order=order).exists():
            raise serializers.ValidationError("Вы уже оставили отзыв на этот заказ.")

        return order