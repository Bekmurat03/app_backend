from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # URL'ы для клиента
    path("", views.OrderListView.as_view(), name="list"),
    
    # 👇 ИЗМЕНЕНО: Теперь этот путь использует нашу новую view для создания заказа и оплаты
    path("create/", views.CreateOrderAndPayView.as_view(), name="create-and-pay"),
    path("calculate-cost/", views.CalculateOrderCostView.as_view(), name="calculate"),

    path("<int:pk>/", views.OrderDetailView.as_view(), name="detail"),
    path("<int:order_id>/cancel/", views.CancelOrderView.as_view(), name="cancel"),
]