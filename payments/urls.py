from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreateCardTokenizationView, PaymentCardViewSet

router = DefaultRouter()
router.register(r'cards', PaymentCardViewSet, basename='paymentcard')

urlpatterns = [
    path('create-tokenization-url/', CreateCardTokenizationView.as_view(), name='create_tokenization_url'),
    path('', include(router.urls)),
]
