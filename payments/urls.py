# payments/urls.py
from django.urls import path
from .views import CreateOrderAndPaymentView, SavedCardListView, PayLinkWebhookView

urlpatterns = [
    path('create-order/', CreateOrderAndPaymentView.as_view(), name='create-order-payment'),
    path('cards/', SavedCardListView.as_view(), name='saved-cards-list'),
    path('webhook/', PayLinkWebhookView.as_view(), name='paylink-webhook'),
]