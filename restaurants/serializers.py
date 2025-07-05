# app_backend/apps/restaurants/serializers.py (ФИНАЛЬНАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ)

from rest_framework import serializers
from .models import Restaurant, DeliveryTariff # 👈 1. Импортируем новую модель тарифов
from menu.serializers import MenuCategorySerializer
from menu.models import MenuCategory

# 👇 2. Создаем новый сериализатор специально для модели тарифов
class DeliveryTariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTariff
        # Указываем, какие поля из тарифа мы хотим отправлять в приложение
        fields = ('name', 'start_time', 'end_time', 'base_fee', 'fee_per_km')


# Этот сериализатор для чтения (когда приложение получает данные о ресторане)
class RestaurantSerializer(serializers.ModelSerializer):
    categories = MenuCategorySerializer(many=True, read_only=True)
    # 👇 3. Добавляем новое поле 'tariffs'
    # Оно будет содержать список всех тарифов для данного ресторана
    tariffs = DeliveryTariffSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            "id",
            "name",
            "description",
            "logo",
            "banner",
            "address",
            "is_approved",
            "categories",
            "latitude", "longitude",
            "tariffs",
            "is_active",
            "phone_number" # 👈 4. Не забываем добавить поле в список
        ]


# Этот сериализатор для записи (он остается без изменений,
# так как тарифы управляются только из админки)
class RestaurantWriteSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=MenuCategory.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Restaurant
        fields = [
            "id",
            "name",
            "description",
            "logo",
            "banner",
            "address",
            "is_approved",
            "categories",
            # "is_active", # и этого тоже
            "latitude", "longitude", "phone_number",
        ]

    def create(self, validated_data):
        categories = validated_data.pop("categories", [])
        restaurant = Restaurant.objects.create(**validated_data)
        restaurant.categories.set(categories)
        return restaurant

    def update(self, instance, validated_data):
        categories = validated_data.pop("categories", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if categories is not None:
            instance.categories.set(categories)

        return instance