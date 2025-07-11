# menu/urls.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GlobalCategoryListView,
    MenuByRestaurantView,
    RestaurantsByCategoryView,
    DishViewSet,
)

# ViewSet для управления блюдами выносим в отдельный роутер для владельцев
owner_router = DefaultRouter()
owner_router.register(r'dishes', DishViewSet, basename='dish')

# Разделяем URL'ы на публичные и для владельцев
# Это более четкая и безопасная структура

# Публичные эндпоинты для клиентов
public_urls = [
    path("categories/", GlobalCategoryListView.as_view(), name="global-category-list"),
    path("categories/<int:category_id>/restaurants/", RestaurantsByCategoryView.as_view(), name="restaurants-by-category"),
    path("restaurants/<int:restaurant_id>/", MenuByRestaurantView.as_view(), name="restaurant-menu"),
]

# Эндпоинты для управления меню (для приложения ресторана)
owner_urls = [
    path("", include(owner_router.urls)),
]

urlpatterns = [
    path("", include(public_urls)),
    path("manage/", include(owner_urls)), # Все URL для управления будут начинаться с /manage/
]