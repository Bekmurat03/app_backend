# app_backend/apps/restaurants/views.py (ФИНАЛЬНАЯ ВЕРСИЯ)

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from .models import Restaurant
from .serializers import RestaurantSerializer, RestaurantWriteSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
# 👇 1. Импортируем необходимые модели и сериализаторы из приложения menu
from menu.models import MenuCategory
from menu.serializers import MenuCategoryWithDishesSerializer
from rest_framework.decorators import api_view, permission_classes


# ------------------- СУЩЕСТВУЮЩИЕ VIEWS (остаются без изменений) -------------------

class ApprovedRestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.filter(is_approved=True)
    serializer_class = RestaurantSerializer

class RestaurantDetailView(generics.RetrieveAPIView):
    queryset = Restaurant.objects.filter(is_approved=True)
    serializer_class = RestaurantSerializer

class MyRestaurantView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return get_object_or_404(Restaurant, owner=self.request.user)
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RestaurantSerializer
        return RestaurantWriteSerializer

class RestaurantCreateView(generics.CreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantWriteSerializer
    permission_classes = [IsAdminUser]
    def perform_create(self, serializer):
        serializer.save()

class ToggleActiveView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        restaurant = get_object_or_404(Restaurant, owner=request.user)
        new_status = request.data.get('is_active')
        if new_status is None:
            return Response({"error": "Поле is_active обязательно."}, status=status.HTTP_400_BAD_REQUEST)
        if new_status is True and (not restaurant.address or not restaurant.latitude):
             return Response({"error": "Чтобы принимать заказы, пожалуйста, укажите ваш адрес и местоположение на карте."}, status=status.HTTP_400_BAD_REQUEST)
        restaurant.is_active = new_status
        restaurant.save()
        serializer = RestaurantSerializer(restaurant)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --- 👇👇👇 ВОТ НОВЫЙ VIEW ДЛЯ ПОЛУЧЕНИЯ МЕНЮ 👇👇👇 ---

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def restaurant_menu_view(request):
    """
    Возвращает меню ресторана, сгруппированное по категориям.
    """
    # Находим ресторан текущего пользователя
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    
    # Теперь мы получаем категории ПРАВИЛЬНО - напрямую из объекта ресторана
    # Django автоматически найдет все категории, связанные с этим рестораном
    # через поле ManyToManyField, которое вы добавили ранее.
    categories = restaurant.categories.prefetch_related('dishes').all()
    
    # Сериализатор MenuCategorySerializer теперь сможет для каждой категории
    # подтянуть вложенные блюда, так как они связаны через related_name="dishes"
    serializer = MenuCategoryWithDishesSerializer(
        categories, 
        many=True, 
        context={'request': request, 'restaurant_id': restaurant.id}
    )
    
    return Response(serializer.data)
