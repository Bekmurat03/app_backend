from rest_framework import serializers
from .models import Restaurant
from menu.serializers import MenuCategorySerializer
from menu.models import MenuCategory


class RestaurantSerializer(serializers.ModelSerializer):
    categories = MenuCategorySerializer(many=True, read_only=True)

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
        ]


# 🔐 Используется для создания и редактирования ресторана (например, в админке или приложении ресторана)
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
