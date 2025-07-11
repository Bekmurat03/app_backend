# app_backend/apps/restaurants/views.py (ОБНОВЛЕННАЯ ВЕРСИЯ)

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Restaurant
from .serializers import RestaurantSerializer, RestaurantWriteSerializer
from menu.serializers import MenuCategoryWithDishesSerializer

# 👇 1. Импортируем наше новое правило доступа
from .permissions import IsRestaurantOwner


class ApprovedRestaurantListView(generics.ListAPIView):
    """
    Отдает список всех одобренных ресторанов для клиентов.
    """
    serializer_class = RestaurantSerializer

    def get_queryset(self):
        # 👇 2. ОПТИМИЗАЦИЯ: Используем prefetch_related.
        # Это самое важное изменение. Теперь Django сделает всего 3 запроса к БД
        # (1 для ресторанов, 1 для всех их категорий, 1 для всех их тарифов)
        # вместо N+1 запросов. Это ускорит загрузку в десятки раз.
        return Restaurant.objects.filter(is_approved=True, is_active=True).prefetch_related(
            'categories', 'tariffs'
        )


class RestaurantDetailView(generics.RetrieveAPIView):
    """
    Отдает детальную информацию об одном ресторане.
    """
    serializer_class = RestaurantSerializer
    # Аналогично оптимизируем запрос и здесь
    queryset = Restaurant.objects.filter(is_approved=True).prefetch_related('categories', 'tariffs')


class MyRestaurantView(generics.RetrieveUpdateAPIView):
    """
    Для владельца: получение и обновление данных своего ресторана.
    """
    # 👇 3. БЕЗОПАСНОСТЬ: Применяем наше новое правило.
    # Теперь DRF автоматически проверит, что пользователь - владелец.
    permission_classes = [IsAuthenticated, IsRestaurantOwner]
    queryset = Restaurant.objects.prefetch_related('categories', 'tariffs').all()

    def get_object(self):
        # Логика поиска объекта остается простой, т.к. проверку прав берет на себя DRF.
        # Мы ищем ресторан, привязанный к пользователю, который делает запрос.
        obj = get_object_or_404(self.get_queryset(), owner=self.request.user)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RestaurantSerializer
        return RestaurantWriteSerializer


class ToggleActiveView(APIView):
    """
    Для владельца: включение/выключение приема заказов.
    """
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    def post(self, request, *args, **kwargs):
        restaurant = get_object_or_404(Restaurant, owner=request.user)
        # Проверку прав теперь можно делегировать нашему permission_classes
        self.check_object_permissions(request, restaurant)

        new_status = request.data.get('is_active')
        if new_status is None:
            return Response({"error": "Поле is_active обязательно."}, status=status.HTTP_400_BAD_REQUEST)

        if new_status is True and (not restaurant.address or not restaurant.latitude):
             return Response({"error": "Чтобы принимать заказы, укажите ваш адрес и местоположение на карте."}, status=status.HTTP_400_BAD_REQUEST)

        restaurant.is_active = new_status
        restaurant.save(update_fields=['is_active']) # Оптимизация: обновляем только одно поле
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RestaurantMenuView(generics.ListAPIView):
    """
    Для владельца: возвращает меню его ресторана, сгруппированное по категориям.
    """
    serializer_class = MenuCategoryWithDishesSerializer
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    def get_queryset(self):
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        # Эта проверка нужна, чтобы убедиться, что пользователь имеет доступ к ресторану
        self.check_object_permissions(self.request, restaurant)
        # Запрос уже был оптимальным, оставляем его
        return restaurant.categories.prefetch_related('dishes').all()

    def get_serializer_context(self):
        # Передаем ID ресторана в сериализатор, чтобы он мог отфильтровать блюда
        context = super().get_serializer_context()
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        context["restaurant_id"] = restaurant.id
        return context


# ВАЖНО: RestaurantCreateView остается без изменений, так как им пользуется только админ.
class RestaurantCreateView(generics.CreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantWriteSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()