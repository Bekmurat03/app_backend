from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Dish, MenuCategory
from .serializers import MenuCategorySerializer, MenuCategoryWithDishesSerializer
from restaurants.models import Restaurant
from restaurants.serializers import RestaurantSerializer
from .serializers import DishWriteSerializer
from rest_framework import viewsets, permissions
from rest_framework import generics

class MenuByRestaurantView(ListAPIView):
    serializer_class = MenuCategoryWithDishesSerializer

    def get_queryset(self):
        restaurant_id = self.kwargs.get("restaurant_id")
        # Возвращаем только те категории, где есть блюда у этого ресторана
        return MenuCategory.objects.filter(
            dishes__restaurant_id=restaurant_id
        ).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["restaurant_id"] = self.kwargs.get("restaurant_id")
        return context

class UniqueCategoriesView(ListAPIView):
    serializer_class = MenuCategorySerializer

    def get_queryset(self):
        return MenuCategory.objects.distinct("name")  # Только уникальные категории по имени

class RestaurantsByCategoryView(APIView):
    def get(self, request, category_id):
        restaurants = Restaurant.objects.filter(categories__id=category_id).distinct()
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)

class GlobalCategoryListView(generics.ListAPIView):
    """
    Отдает список всех уникальных категорий меню для использования на главной странице клиента.
    """
    queryset = MenuCategory.objects.order_by('name').distinct('name')
    serializer_class = MenuCategorySerializer
    permission_classes = [permissions.AllowAny] # Разрешаем доступ всем

class DishViewSet(viewsets.ModelViewSet):
    serializer_class = DishWriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Dish.objects.filter(restaurant__owner=user)

    def perform_create(self, serializer):
        user = self.request.user
        restaurant = user.restaurants.first()
        serializer.save(restaurant=restaurant)