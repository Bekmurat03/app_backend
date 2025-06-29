from django.urls import path
from .views import PromoBannerListView, ValidatePromoCodeView

urlpatterns = [
    path('', PromoBannerListView.as_view()),
    path("validate/", ValidatePromoCodeView.as_view(), name="validate-promo"),
]
