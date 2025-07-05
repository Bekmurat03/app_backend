# courier/urls.py
from django.urls import path
from .views import AvailableOrdersView, CourierAcceptOrderView, CourierOrderHistoryView, CourierStatsView, CurrentOrderView, DocumentUploadView, OrderDeliveredView, OrderPickedUpView, OrderTrackingView, ToggleOnlineStatusView, UpdateCourierLocationView

urlpatterns = [
    # Этот URL будет использоваться для отправки документов
    path('upload-documents/', DocumentUploadView.as_view(), name='courier-document-upload'),
    path("orders/current/", CurrentOrderView.as_view(), name="courier-current-order"),
     # 👇👇👇 ВОТ НЕДОСТАЮЩИЕ ПУТИ 👇👇👇
    path("available/", AvailableOrdersView.as_view(), name="courier-available-orders"),
    path("accept/<int:order_id>/", CourierAcceptOrderView.as_view(), name="courier-accept-order"),
    path("order/<int:order_id>/picked_up/", OrderPickedUpView.as_view(), name="courier-order-picked-up"),
    path("order/<int:order_id>/delivered/", OrderDeliveredView.as_view(), name="courier-order-delivered"),
     path('update-location/', UpdateCourierLocationView.as_view(), name='update-courier-location'),
    path('orders/<int:order_id>/track/', OrderTrackingView.as_view(), name='order-tracking'),
    path('toggle-online/', ToggleOnlineStatusView.as_view(), name='courier-toggle-online'),
    path('history/', CourierOrderHistoryView.as_view(), name='courier-history'),
    path('stats/', CourierStatsView.as_view(), name='courier-stats'),
]