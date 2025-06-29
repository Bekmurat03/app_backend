from django.urls import path
from .views import MarkOrderReadyView, OrderDetailView, OrderListCreateView, RestaurantOrdersView

urlpatterns = [
    # 📦 Заказы клиента: список и создание
    path("", OrderListCreateView.as_view(), name="order-list-create"),

    # 👨‍🍳 Заказы, относящиеся к ресторану (для владельца ресторана)
    path("restaurant/", RestaurantOrdersView.as_view(), name="restaurant-orders"),
    path("restaurant/orders/<int:order_id>/mark_ready/", MarkOrderReadyView.as_view(), name="order-mark-ready"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
]
