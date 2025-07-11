# reviews/views.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
from rest_framework import viewsets, permissions, generics
from django.shortcuts import get_object_or_404
from .models import Review
from .serializers import ReviewCreateSerializer, PublicReviewSerializer
from .permissions import IsReviewOwner
from restaurants.models import Restaurant

class MyReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления СВОИМИ отзывами (создать, посмотреть, изменить, удалить).
    """
    serializer_class = ReviewCreateSerializer
    # Применяем наши новые права доступа
    permission_classes = [permissions.IsAuthenticated, IsReviewOwner]

    def get_queryset(self):
        """Пользователь видит и может управлять только своими отзывами."""
        return Review.objects.filter(user=self.request.user).select_related('order', 'order__restaurant')

    def perform_create(self, serializer):
        """При создании отзыва привязываем его к текущему пользователю."""
        serializer.save(user=self.request.user)


class RestaurantReviewListView(generics.ListAPIView):
    """
    Публичный эндпоинт для просмотра всех отзывов для конкретного ресторана.
    """
    serializer_class = PublicReviewSerializer
    permission_classes = [permissions.AllowAny] # Доступно всем

    def get_queryset(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        # Оптимизируем запрос, подтягивая связанных пользователей
        return Review.objects.filter(order__restaurant=restaurant).select_related('user').order_by('-created_at')