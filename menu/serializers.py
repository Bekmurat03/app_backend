from rest_framework import serializers
from .models import MenuCategory, Dish

class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'image']

class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ['id', 'name', 'description', 'price', 'image']

class MenuCategoryWithDishesSerializer(serializers.ModelSerializer):
    dishes = serializers.SerializerMethodField()

    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'image', 'dishes']

    def get_dishes(self, obj):
        restaurant_id = self.context.get("restaurant_id")
        if not restaurant_id:
            return []  # безопасно возвращаем пустой список, если restaurant_id не передан
        dishes = obj.dishes.filter(restaurant__id=restaurant_id)
        return DishSerializer(dishes, many=True).data
class DishWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ['id', 'name', 'description', 'price', 'image', 'category']

    def create(self, validated_data):
        # удалим restaurant из validated_data, если он есть
        restaurant = validated_data.pop('restaurant', None)

        # получаем ресторан текущего пользователя
        if not restaurant:
            user = self.context['request'].user
            restaurant = user.restaurants.first()

        return Dish.objects.create(restaurant=restaurant, **validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance