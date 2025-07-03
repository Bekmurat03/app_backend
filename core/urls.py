# apps/core/urls.py (ФИНАЛЬНАЯ ИСПРАВЛЕННАЯ ВЕРСИЯ)

from django.urls import path, include  # 👈 УБЕДИТЕСЬ, ЧТО include ИМПОРТИРОВАН
from .views import ChangePasswordView, PhoneLoginView, RegisterView, TogglePushView, UserDetailView, AddressViewSet, toggle_push_notifications
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', PhoneLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('toggle-push/', toggle_push_notifications, name='toggle-push'),

    # 👇👇👇 ЭТОЙ СТРОКИ НЕ ХВАТАЛО 👇👇👇
    # Она добавляет путь /api/addresses/ к остальным
    path('', include(router.urls)),
]