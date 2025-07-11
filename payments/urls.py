# payments/urls.py (ПОЛНЫЙ ОБНОВЛЕННЫЙ КОД)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreateCardTokenizationView, CheckTokenizationStatusView, PaymentCardViewSet

router = DefaultRouter()
router.register(r'cards', PaymentCardViewSet, basename='paymentcard')

urlpatterns = [
    path('create-tokenization-url/', CreateCardTokenizationView.as_view(), name='create_tokenization_url'),
    # 👇 НОВЫЙ URL ДЛЯ ПРОВЕРКИ
    path('check-tokenization-status/<uuid:attempt_id>/', CheckTokenizationStatusView.as_view(), name='check_tokenization_status'),
    path('', include(router.urls)),
]