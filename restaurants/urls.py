# app_backend/apps/restaurants/urls.py (ИСПРАВЛЕННАЯ ВЕРСИЯ)

from django.urls import path
from .views import (
    ApprovedRestaurantListView,
    RestaurantDetailView,
    MyRestaurantView,
    RestaurantCreateView,
    ToggleActiveView,
    RestaurantMenuView # 👈 ИСПРАВЛЕНО: Импортируем правильный класс
)

urlpatterns = [
    # Публичные URL для клиентов
    path("", ApprovedRestaurantListView.as_view(), name="restaurant-list"),
    path("<int:pk>/", RestaurantDetailView.as_view(), name="restaurant-detail"),

    # URL для владельца ресторана
    path("me/", MyRestaurantView.as_view(), name="my-restaurant"),
    path("me/toggle-active/", ToggleActiveView.as_view(), name="toggle-restaurant-active"),
    
    # ИСПРАВЛЕНО: Используем класс RestaurantMenuView с .as_view()
    path("me/menu/", RestaurantMenuView.as_view(), name="my-restaurant-menu"),

    # URL для администраторов
    path("create/", RestaurantCreateView.as_view(), name="restaurant-create"),
]