# app_backend/apps/restaurants/serializers.py (ОБНОВЛЕННАЯ ВЕРСИЯ)

from rest_framework import serializers
from django.db.models import Avg # Для подсчета среднего рейтинга
from .models import Restaurant, DeliveryTariff
from menu.serializers import MenuCategorySerializer
from menu.models import MenuCategory


class DeliveryTariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTariff
        fields = ('name', 'start_time', 'end_time', 'base_fee', 'fee_per_km')


class RestaurantSerializer(serializers.ModelSerializer):
    categories = MenuCategorySerializer(many=True, read_only=True)
    tariffs = DeliveryTariffSerializer(many=True, read_only=True)

    # 👇 4. ПРИМЕР ПРОДВИНУТОГО ПОЛЯ: Вычисляемый рейтинг
    # Это поле не хранится в БД, а считается "на лету".
    # Для его работы нужна модель Review, которая у вас уже есть.
    rating = serializers.SerializerMethodField()

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
            "phone_number",
            "rating", # 👈 Добавили новое поле в список
        ]

    def get_rating(self, obj):
        # `obj` - это экземпляр ресторана.
        # Находим все заказы этого ресторана, у которых есть отзыв, и считаем средний рейтинг.
        # Метод aggregate намного эффективнее, чем получать все отзывы и считать среднее в Python.
        avg_rating = obj.orders.filter(review__isnull=False).aggregate(Avg('review__rating'))['review__rating__avg']
        # Возвращаем 0, если отзывов еще нет.
        return round(avg_rating, 1) if avg_rating else 0.0


# Сериализатор для записи остается без изменений, он отлично спроектирован.
class RestaurantWriteSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        queryset=MenuCategory.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Restaurant
        # Поля для записи не меняем
        fields = [
            "id", "name", "description", "logo", "banner",
            "address", "is_approved", "categories",
            "latitude", "longitude", "phone_number",
        ]

    def create(self, validated_data):
        categories = validated_data.pop("categories", [])
        restaurant = Restaurant.objects.create(**validated_data)
        restaurant.categories.set(categories)
        return restaurant

    def update(self, instance, validated_data):
        categories = validated_data.pop("categories", None)
        # Этот цикл - хороший способ обновить только те поля, что были переданы
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if categories is not None:
            instance.categories.set(categories)

        return instance