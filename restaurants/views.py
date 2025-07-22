from rest_framework import generics, status, filters # 👈 1. Убеждаемся, что filters импортирован
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Restaurant
from .serializers import RestaurantSerializer, RestaurantWriteSerializer
from menu.serializers import MenuCategoryWithDishesSerializer
from .permissions import IsRestaurantOwner


class ApprovedRestaurantListView(generics.ListAPIView):
    """
    Отдает список всех одобренных ресторанов для клиентов.
    Поддерживает поиск по названию ресторана и названию блюд.
    """
    serializer_class = RestaurantSerializer
    
    # 👇 2. ДОБАВЛЯЕМ ФИЛЬТРЫ ДЛЯ ПОИСКА
    filter_backends = [filters.SearchFilter]
    # По каким полям будем искать: по названию ресторана и по названиям связанных с ним блюд.
    search_fields = ['name', 'dishes__name']

    def get_queryset(self):
        # Оптимизация запроса остается, это очень важно для производительности
        return Restaurant.objects.filter(is_approved=True, is_active=True).prefetch_related(
            'categories', 'tariffs'
        )


class RestaurantDetailView(generics.RetrieveAPIView):
    """
    Отдает детальную информацию об одном ресторане.
    """
    serializer_class = RestaurantSerializer
    queryset = Restaurant.objects.filter(is_approved=True).prefetch_related('categories', 'tariffs')


class MyRestaurantView(generics.RetrieveUpdateAPIView):
    """
    Для владельца: получение и обновление данных своего ресторана.
    """
    permission_classes = [IsAuthenticated, IsRestaurantOwner]
    queryset = Restaurant.objects.prefetch_related('categories', 'tariffs').all()

    def get_object(self):
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
        self.check_object_permissions(request, restaurant)

        new_status = request.data.get('is_active')
        if new_status is None:
            return Response({"error": "Поле is_active обязательно."}, status=status.HTTP_400_BAD_REQUEST)

        if new_status is True and (not restaurant.address or not restaurant.latitude):
             return Response({"error": "Чтобы принимать заказы, укажите ваш адрес и местоположение на карте."}, status=status.HTTP_400_BAD_REQUEST)

        restaurant.is_active = new_status
        restaurant.save(update_fields=['is_active'])
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
        self.check_object_permissions(self.request, restaurant)
        return restaurant.categories.prefetch_related('dishes').all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        restaurant = get_object_or_404(Restaurant, owner=self.request.user)
        context["restaurant_id"] = restaurant.id
        return context


class RestaurantCreateView(generics.CreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantWriteSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()