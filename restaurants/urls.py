# app_backend/apps/restaurants/urls.py (ФИНАЛЬНАЯ ВЕРСИЯ)

from django.urls import path
from .views import (
    ApprovedRestaurantListView,
    RestaurantDetailView,
    MyRestaurantView,
    RestaurantCreateView,
    ToggleActiveView,
    restaurant_menu_view # 👈 Убеждаемся, что новый view импортирован
)

urlpatterns = [
    # Публичные URL
    path("", ApprovedRestaurantListView.as_view(), name="restaurant-list"),
    path("<int:pk>/", RestaurantDetailView.as_view(), name="restaurant-detail"),

    # URL для владельца ресторана
    path("me/", MyRestaurantView.as_view(), name="my-restaurant"),
    path("me/toggle-active/", ToggleActiveView.as_view(), name="toggle-restaurant-active"),
    
    # 👇 ИСПРАВЛЕНО: Этот путь теперь будет работать
    path("menu/", restaurant_menu_view, name="restaurant-menu"),
]