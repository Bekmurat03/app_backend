# promos/urls.py (ОБНОВЛЕННАЯ ВЕРСИЯ)
from django.urls import path
from .views import PromoBannerListView, ValidatePromoCodeView, ApplyPromoCodeView

app_name = 'promos'

urlpatterns = [
    path('banners/', PromoBannerListView.as_view(), name="banners-list"),
    path("validate/", ValidatePromoCodeView.as_view(), name="validate-promo"),
    path("apply/", ApplyPromoCodeView.as_view(), name="apply-promo"), 
    
]