from django.urls import path
from .views import (
    ApprovedRestaurantListView,
    RestaurantDetailView,
    MyRestaurantView,
    RestaurantCreateView,
    restaurant_menu_view,
)

urlpatterns = [
    # 📱 Клиенты видят только одобренные рестораны
    path("", ApprovedRestaurantListView.as_view(), name="restaurant-list"),
    path("<int:pk>/", RestaurantDetailView.as_view(), name="restaurant-detail"),

    # 👨‍🍳 Ресторатор может посмотреть и отредактировать свой ресторан
    path("me/", MyRestaurantView.as_view(), name="my-restaurant"),

    # 🔐 Только админ может создавать рестораны через админ-панель
    path("admin/create/", RestaurantCreateView.as_view(), name="restaurant-create"),

    # 🍽 Меню ресторана (для владельца ресторана)
    path("menu/", restaurant_menu_view, name="restaurant-menu"),
]
