# menu/views.py (ОБНОВЛЕННАЯ ВЕРСИЯ)

from rest_framework import generics, viewsets, permissions
from django.db.models import Prefetch, Count
from django.shortcuts import get_object_or_404

from .models import Dish, MenuCategory
from .serializers import MenuCategorySerializer, DishSerializer, MenuCategoryWithDishesSerializer
from restaurants.models import Restaurant
from restaurants.serializers import RestaurantSerializer
from .permissions import IsDishOwner # 👈 1. Импортируем наше новое правило


# --- VIEWS ДЛЯ КЛИЕНТОВ (публичные) ---

class GlobalCategoryListView(generics.ListAPIView):
    """
    Отдает список всех категорий, в которых есть хотя бы один ресторан.
    """
    serializer_class = MenuCategorySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # 2. ОПТИМИЗАЦИЯ: Аннотируем количество ресторанов и фильтруем.
        # Это эффективнее, чем .distinct() на больших объемах данных.
        return MenuCategory.objects.annotate(
            num_restaurants=Count('restaurants')
        ).filter(num_restaurants__gt=0)


class RestaurantsByCategoryView(generics.ListAPIView):
    """
    Отдает список ресторанов для выбранной категории.
    """
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        # 3. ОПТИМИЗАЦИЯ: Сразу подтягиваем связанные категории и тарифы
        return Restaurant.objects.filter(
            categories__id=category_id, is_approved=True, is_active=True
        ).prefetch_related('categories', 'tariffs')


class MenuByRestaurantView(generics.ListAPIView):
    """
    Отдает полное меню ресторана, сгруппированное по категориям.
    """
    serializer_class = MenuCategoryWithDishesSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, is_approved=True)

        # 4. ГЛАВНАЯ ОПТИМИЗАЦИЯ:
        # Мы получаем категории, но сразу же "подгружаем" в них только те блюда,
        # которые относятся к нужному ресторану и доступны.
        # Это решает проблему N+1 запросов.
        return MenuCategory.objects.prefetch_related(
            Prefetch(
                'dishes',
                queryset=Dish.objects.filter(restaurant=restaurant, is_available=True)
            )
        ).filter(dishes__restaurant=restaurant).distinct()


# --- VIEWSET ДЛЯ МЕНЕДЖЕРА РЕСТОРАНА ---

class DishViewSet(viewsets.ModelViewSet):
    """
    API для управления блюдами (CRUD) для владельца ресторана.
    """
    serializer_class = DishSerializer
    # 5. БЕЗОПАСНОСТЬ: Применяем наше новое правило доступа.
    # IsAuthenticated - для всех запросов, IsDishOwner - для конкретных объектов (update, delete).
    permission_classes = [permissions.IsAuthenticated, IsDishOwner]

    def get_queryset(self):
        # Пользователь видит блюда только из своих ресторанов
        if hasattr(self.request.user, 'restaurants'):
            return Dish.objects.filter(restaurant__in=self.request.user.restaurants.all())
        return Dish.objects.none()

    def perform_create(self, serializer):
        # При создании блюда автоматически привязываем его к ресторану владельца.
        # В реальном приложении с несколькими ресторанами у владельца
        # нужно было бы передавать ID ресторана в запросе.
        restaurant = self.request.user.restaurants.first()
        if restaurant:
            serializer.save(restaurant=restaurant)
        else:
            raise serializers.ValidationError("У вас нет ресторана для добавления блюда.")