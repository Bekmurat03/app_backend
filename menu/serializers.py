# menu/serializers.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
from rest_framework import serializers
from .models import MenuCategory, Dish

class MenuCategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий меню."""
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'image']


class DishSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для блюд (для чтения)."""
    class Meta:
        model = Dish
        fields = ['id', 'name', 'description', 'price', 'image', 'is_available', 'category']


class MenuCategoryWithDishesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения категории вместе со всеми ее блюдами
    (для конкретного ресторана).
    """
    # Теперь dishes не SerializerMethodField, а вложенный сериализатор.
    # Данные для него мы подготовим во view с помощью prefetch_related.
    dishes = DishSerializer(many=True, read_only=True)

    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'image', 'dishes']
class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__' # Включаем все поля из модели Dish