# reviews/urls.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MyReviewViewSet, RestaurantReviewListView

router = DefaultRouter()
# Регистрируем ViewSet для управления своими отзывами по пути /my-reviews/
router.register(r'my-reviews', MyReviewViewSet, basename='my-review')

urlpatterns = [
    # URL для получения списка отзывов для конкретного ресторана
    path('restaurants/<int:restaurant_id>/reviews/', RestaurantReviewListView.as_view(), name='restaurant-reviews'),
    # URL'ы для управления своими отзывами
    path('', include(router.urls)),
]