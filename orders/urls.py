# orders/urls.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
from django.urls import path
from .views import (
    CreateOrderView,
    CreateAndPayOrderView,
    OrderListCreateView,
    OrderDetailView,
    CancelOrderView,
    PayOrderView,
    RestaurantOrderListView,
    RestaurantManageOrderView,
    # Оставляем views для платежей
    CreatePaymentView,
    PayLinkWebhookView,
    RefundPaymentView,
    CalculateOrderTotalsView
)

app_name = 'orders'

urlpatterns = [
    # --- URL для КЛИЕНТА ---
    path("", OrderListCreateView.as_view(), name="list_create"),
    path("<int:pk>/", OrderDetailView.as_view(), name="detail"),
    path("calculate-totals/", CalculateOrderTotalsView.as_view(), name="order_calculate_totals"),
    path("create/", CreateOrderView.as_view(), name="order_create"),
    path("<int:order_id>/cancel/", CancelOrderView.as_view(), name="cancel"),
    path("create-and-pay/", CreateAndPayOrderView.as_view(), name="order_create_and_pay"),

    # --- URL для РЕСТОРАНА ---
    path("restaurant/", RestaurantOrderListView.as_view(), name="restaurant_list"),
    path("restaurant/<int:order_id>/manage/", RestaurantManageOrderView.as_view(), name="restaurant_manage"),

    # --- URL для ПЛАТЕЖЕЙ (можно вынести в отдельное приложение 'payments') ---
    path('<int:pk>/create-payment/', CreatePaymentView.as_view(), name='create_payment'),
    path('payment-webhook/', PayLinkWebhookView.as_view(), name='payment_webhook'),
    path('<int:pk>/refund/', RefundPaymentView.as_view(), name='refund_payment'),
    path('<int:pk>/pay/', PayOrderView.as_view(), name='pay_order'),
]