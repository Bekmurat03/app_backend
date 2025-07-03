# orders/urls.py
from django.urls import path
from .views import (
    OrderListCreateView,
    RestaurantOrdersView,
    AcceptOrderView,
    RejectOrderView,
    UpdateOrderStatusView,
    OrderDetailView,CancelOrderView
)

urlpatterns = [
    # 📦 Для клиента
    path("", OrderListCreateView.as_view(), name="order-list-create"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail-client"),
    path("<int:order_id>/cancel/", CancelOrderView.as_view(), name="order-cancel-client"),
    # 👨‍🍳 Для ресторана
    path("restaurant/", RestaurantOrdersView.as_view(), name="restaurant-orders-list"),
    path("restaurant/<int:order_id>/accept/", AcceptOrderView.as_view(), name="order-accept"),
    path("restaurant/<int:order_id>/reject/", RejectOrderView.as_view(), name="order-reject"),
    path("restaurant/<int:order_id>/update_status/", UpdateOrderStatusView.as_view(), name="order-update-status"),
]