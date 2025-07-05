# app_backend/apps/core/urls.py (ФИНАЛЬНАЯ ВЕРСИЯ)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    PhoneLoginView,
    UserDetailView,
    ChangePasswordView,
    AddressViewSet,
    TogglePushNotificationView # 👈 Используем единый, правильный View
)

# Создаем router только для адресов
router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    # Аутентификация и регистрация
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', PhoneLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Управление пользователем
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # 👇 ИСПРАВЛЕНО: Путь 'toggle-push/' теперь использует правильный обработчик
    path('toggle-push/', TogglePushNotificationView.as_view(), name='toggle-push'),

    # URL для адресов (создает /api/addresses/, /api/addresses/<id>/ и т.д.)
    path('', include(router.urls)),
]