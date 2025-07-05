# app_backend/apps/core/views.py (ФИНАЛЬНАЯ ВЕРСИЯ)

from rest_framework import generics, status, viewsets, permissions
from .models import Address
# 👇 1. Убедимся, что импортируем правильные сериализаторы
from .serializers import (
    AddressSerializer, 
    ChangePasswordSerializer, 
    PhoneTokenObtainPairSerializer, 
    RegisterSerializer, 
    UserSerializer
)
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class PhoneLoginView(TokenObtainPairView):
    serializer_class = PhoneTokenObtainPairSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    Для получения и обновления данных текущего пользователя.
    Теперь использует единый UserSerializer.
    """
    serializer_class = UserSerializer # 👈 2. Используем единый, правильный сериализатор
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Пароль успешно изменен."}, status=status.HTTP_200_OK)


class AddressViewSet(viewsets.ModelViewSet):
    """
    API для управления адресами текущего пользователя.
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user).order_by('-is_primary', 'title')

    def perform_create(self, serializer):
        is_first_address = not Address.objects.filter(user=self.request.user).exists()
        serializer.save(user=self.request.user, is_primary=is_first_address)

# --- 👇 3. Оставляем только ОДНУ, правильную реализацию для переключения уведомлений ---
class TogglePushNotificationView(APIView):
    """
    Переключает включение/выключение основных уведомлений.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        # Мы просто меняем значение на противоположное
        user.is_push_enabled = not user.is_push_enabled
        user.save(update_fields=['is_push_enabled'])
        return Response({
            "is_push_enabled": user.is_push_enabled
        }, status=status.HTTP_200_OK)