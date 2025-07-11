from django.urls import path, include
from .views import (
    DocumentUploadView,
    ToggleOnlineStatusView,
    UpdateCourierLocationView,
    AvailableOrdersView,
    CourierAcceptOrderView,
    CurrentOrderView,
    UpdateDeliveryStatusView, # 👈 Импортируем наш перенесенный view
    CourierOrderHistoryView,
    CourierStatsView,
    OrderTrackingView,
)

profile_urls = [
    path('documents/', DocumentUploadView.as_view(), name='document-upload'),
    path('status/toggle-online/', ToggleOnlineStatusView.as_view(), name='toggle-online'),
    path('location/update/', UpdateCourierLocationView.as_view(), name='update-location'),
    path('stats/', CourierStatsView.as_view(), name='stats'),
]

orders_urls = [
    path('available/', AvailableOrdersView.as_view(), name='available-orders'),
    path('current/', CurrentOrderView.as_view(), name='current-order'),
    path('history/', CourierOrderHistoryView.as_view(), name='order-history'),
    path('<int:order_id>/accept/', CourierAcceptOrderView.as_view(), name='accept-order'),
    # 👇 ВОТ НАШ НОВЫЙ URL, КОТОРЫЙ БУДЕТ ИСПОЛЬЗОВАТЬ ПРИЛОЖЕНИЕ КУРЬЕРА
    path('<int:order_id>/update-status/', UpdateDeliveryStatusView.as_view(), name='update-delivery-status'),
]

client_urls = [
    path('track/<int:order_id>/', OrderTrackingView.as_view(), name='order-tracking'),
]

urlpatterns = [
    path('profile/', include(profile_urls)),
    path('orders/', include(orders_urls)),
    path('', include(client_urls)),
]